"""Client API pubblica Binance (spot + funding futures). Nessuna API key richiesta."""
import logging

import httpx
import pandas as pd

from config import (
    CRYPTO_TOP_N,
    LEVERAGED_SUFFIXES,
    MIN_CRYPTO_QUOTE_VOLUME,
    STABLECOINS,
)

log = logging.getLogger(__name__)

SPOT = "https://api.binance.com"
FUTURES = "https://fapi.binance.com"

_client = httpx.Client(timeout=20.0)


def _get(url: str, params: dict | None = None):
    resp = _client.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


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


def _klines_to_df(raw: list) -> pd.DataFrame:
    df = pd.DataFrame(
        raw,
        columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "qv", "trades", "tbb", "tbq", "ignore",
        ],
    )
    df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
    df.index = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df[["open", "high", "low", "close", "volume"]]


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
    except Exception:
        return None
