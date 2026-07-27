"""Client API pubblica Binance (spot + funding futures). Nessuna API key richiesta."""
import json
import logging
import time
from pathlib import Path

import httpx
import pandas as pd

from config import (
    CACHE_DIR,
    CRYPTO_TOP_N,
    FUTURES_KLINES_CACHE_TTL_S,
    LEVERAGED_SUFFIXES,
    MIN_CRYPTO_QUOTE_VOLUME,
    OI_HIST_CACHE_TTL_S,
    OI_HIST_PERIOD,
    STABLECOINS,
)

log = logging.getLogger(__name__)

SPOT = "https://api.binance.com"
FUTURES = "https://fapi.binance.com"
# Endpoint dati futures (OI hist): stesso host fapi
FUTURES_DATA = "https://fapi.binance.com"

_client = httpx.Client(timeout=20.0)

MAX_RETRIES = 3
_BASE_BACKOFF_S = 1.0

_OI_CACHE_DIR = CACHE_DIR / "oi_hist"
_FUT_KLINES_CACHE_DIR = CACHE_DIR / "futures_klines"
_OI_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_FUT_KLINES_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _get(url: str, params: dict | None = None):
    """GET con retry a backoff esponenziale (3 tentativi) su 429/5xx e timeout.

    Gli altri errori HTTP (4xx) non sono transitori e vengono rilanciati subito."""
    delay = _BASE_BACKOFF_S
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = _client.get(url, params=params)
        except httpx.TimeoutException:
            if attempt == MAX_RETRIES:
                raise
            log.warning(
                "timeout su %s (tentativo %d/%d), retry tra %.1fs",
                url, attempt, MAX_RETRIES, delay,
            )
            time.sleep(delay)
            delay *= 2
            continue
        if resp.status_code == 429 or resp.status_code >= 500:
            if attempt == MAX_RETRIES:
                resp.raise_for_status()
            log.warning(
                "HTTP %d su %s (tentativo %d/%d), retry tra %.1fs",
                resp.status_code, url, attempt, MAX_RETRIES, delay,
            )
            time.sleep(delay)
            delay *= 2
            continue
        resp.raise_for_status()
        return resp.json()


def _cache_read(path: Path, ttl_s: float):
    if not path.exists():
        return None
    age = time.time() - path.stat().st_mtime
    if age > ttl_s:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _cache_write(path: Path, payload) -> None:
    try:
        path.write_text(json.dumps(payload), encoding="utf-8")
    except OSError as exc:
        log.warning("cache write %s fallita: %s", path, exc)


def top_usdt_symbols(n: int = CRYPTO_TOP_N) -> list[str]:
    """Top N coppie USDT spot per quote volume 24h, escluse stablecoin e token a leva."""
    data = _get(f"{SPOT}/api/v3/ticker/24hr")
    rows = []
    for t in data:
        sym = t["symbol"]
        if not sym.endswith("USDT"):
            continue
        base = sym[:-4]
        if base in STABLECOINS or base.endswith(LEVERAGED_SUFFIXES):
            continue
        qv = float(t.get("quoteVolume", 0))
        if qv < MIN_CRYPTO_QUOTE_VOLUME:
            continue
        rows.append((sym, qv))
    rows.sort(key=lambda x: x[1], reverse=True)
    return [s for s, _ in rows[:n]]


def _klines_to_df(raw: list, *, keep_taker: bool = False) -> pd.DataFrame:
    df = pd.DataFrame(
        raw,
        columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "qv", "trades", "tbb", "tbq", "ignore",
        ],
    )
    cols = {"open": float, "high": float, "low": float, "close": float, "volume": float}
    if keep_taker:
        cols["tbb"] = float
    df = df.astype(cols)
    df.index = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    out_cols = ["open", "high", "low", "close", "volume"]
    if keep_taker:
        out_cols.append("tbb")
    return df[out_cols]


def klines(symbol: str, interval: str = "1d", limit: int = 400) -> pd.DataFrame:
    """OHLCV come DataFrame indicizzato per datetime (solo candele chiuse)."""
    raw = _get(
        f"{SPOT}/api/v3/klines",
        params={"symbol": symbol, "interval": interval, "limit": limit},
    )
    if not raw:
        return pd.DataFrame()
    # L'ultima candela è ancora in formazione: la teniamo ma il chiamante lo sa.
    return _klines_to_df(raw)


def klines_range(
    symbol: str,
    interval: str = "1d",
    start_ms: int | None = None,
    end_ms: int | None = None,
) -> pd.DataFrame:
    """Storico OHLCV paginato oltre il limite di 1000 candele per richiesta.

    Usato dal backtester per scaricare anni di daily. Ritorna barre ordinate,
    senza duplicati; l'ultima può essere in formazione come per klines().
    """
    frames: list[pd.DataFrame] = []
    cursor = start_ms
    while True:
        params: dict = {"symbol": symbol, "interval": interval, "limit": 1000}
        if cursor is not None:
            params["startTime"] = cursor
        if end_ms is not None:
            params["endTime"] = end_ms
        raw = _get(f"{SPOT}/api/v3/klines", params=params)
        if not raw:
            break
        frames.append(_klines_to_df(raw))
        if len(raw) < 1000:
            break
        cursor = int(raw[-1][0]) + 1
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames)
    return out[~out.index.duplicated(keep="first")].sort_index()


def funding_rate(symbol: str) -> float | None:
    """Ultimo funding rate del perpetual (None se il perp non esiste)."""
    try:
        data = _get(f"{FUTURES}/fapi/v1/premiumIndex", params={"symbol": symbol})
        return float(data["lastFundingRate"])
    except Exception as exc:
        log.warning("funding rate %s non disponibile: %s", symbol, exc)
        return None


def open_interest_hist(
    symbol: str,
    period: str = OI_HIST_PERIOD,
    limit: int = 30,
    *,
    use_cache: bool = True,
) -> pd.Series:
    """Serie OI da GET /futures/data/openInterestHist (cache disco TTL 1h per period 4h).

    Ritorna Series float indicizzata per timestamp UTC. Vuota se non disponibile.
    """
    cache_path = _OI_CACHE_DIR / f"{symbol}_{period}_{limit}.json"
    raw = _cache_read(cache_path, OI_HIST_CACHE_TTL_S) if use_cache else None
    if raw is None:
        try:
            raw = _get(
                f"{FUTURES_DATA}/futures/data/openInterestHist",
                params={"symbol": symbol, "period": period, "limit": limit},
            )
            if use_cache and raw:
                _cache_write(cache_path, raw)
        except Exception as exc:
            log.warning("OI hist %s non disponibile: %s", symbol, exc)
            return pd.Series(dtype=float)
    if not raw:
        return pd.Series(dtype=float)
    idx = pd.to_datetime([int(r["timestamp"]) for r in raw], unit="ms", utc=True)
    vals = [float(r["sumOpenInterest"]) for r in raw]
    return pd.Series(vals, index=idx, name="oi").sort_index()


def futures_klines(
    symbol: str,
    interval: str = "4h",
    limit: int = 100,
    *,
    use_cache: bool = True,
) -> pd.DataFrame:
    """OHLCV futures con colonna tbb (taker buy base volume) per CVD.

    Cache disco TTL FUTURES_KLINES_CACHE_TTL_S.
    """
    cache_path = _FUT_KLINES_CACHE_DIR / f"{symbol}_{interval}_{limit}.json"
    raw = _cache_read(cache_path, FUTURES_KLINES_CACHE_TTL_S) if use_cache else None
    if raw is None:
        try:
            raw = _get(
                f"{FUTURES}/fapi/v1/klines",
                params={"symbol": symbol, "interval": interval, "limit": limit},
            )
            if use_cache and raw:
                _cache_write(cache_path, raw)
        except Exception as exc:
            log.warning("futures klines %s non disponibili: %s", symbol, exc)
            return pd.DataFrame()
    if not raw:
        return pd.DataFrame()
    return _klines_to_df(raw, keep_taker=True)
