"""Dati azionari via Yahoo Finance (gratuito).

Costituenti (fonti gratuite, Wikipedia blocca le richieste automatiche):
- S&P 500: dataset GitHub `datasets/s-and-p-500-companies` (CSV)
- Nasdaq 100: API pubblica api.nasdaq.com
"""
import csv
import io
import json
import logging
import time
from datetime import datetime, time as dtime
from zoneinfo import ZoneInfo

import httpx
import pandas as pd
import yfinance as yf

from config import CACHE_DIR

log = logging.getLogger(__name__)

NY_TZ = ZoneInfo("America/New_York")
SESSION_CLOSE = dtime(16, 0)


def _drop_unclosed_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Scarta la barra daily di oggi se la sessione USA non è ancora chiusa.

    Durante l'orario di cassa Yahoo include la barra parziale del giorno:
    usarla contamina RVOL (volume sottostimato), trigger/stop (high/low non
    definitivi, repainting a ogni scan) e tutti gli indicatori. Il client
    crypto tronca già la candela in formazione: qui l'equivalente per le stock.
    """
    if df.empty:
        return df
    now_ny = datetime.now(NY_TZ)
    last_ts = df.index[-1]
    last_date = last_ts.tz_convert(NY_TZ).date() if last_ts.tzinfo else last_ts.date()
    if last_date == now_ny.date() and now_ny.time() < SESSION_CLOSE:
        return df.iloc[:-1]
    return df

UNIVERSE_CACHE = CACHE_DIR / "universe_stocks.json"
UNIVERSE_MAX_AGE_S = 7 * 24 * 3600  # refresh settimanale

SP500_CSV = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"
NDX_API = "https://api.nasdaq.com/api/quote/list-type/nasdaq100"
_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "application/json"}


def _fetch_sp500() -> list[str]:
    resp = httpx.get(SP500_CSV, timeout=30.0, follow_redirects=True)
    resp.raise_for_status()
    reader = csv.DictReader(io.StringIO(resp.text))
    return [row["Symbol"].strip() for row in reader if row.get("Symbol")]


def _fetch_nasdaq100() -> list[str]:
    resp = httpx.get(NDX_API, headers=_HEADERS, timeout=30.0)
    resp.raise_for_status()
    rows = resp.json()["data"]["data"]["rows"]
    return [r["symbol"].strip() for r in rows if r.get("symbol")]


def stock_universe() -> list[str]:
    """S&P 500 + Nasdaq 100, simboli in formato Yahoo (BRK.B -> BRK-B). Cache 7 giorni."""
    if UNIVERSE_CACHE.exists():
        cached = json.loads(UNIVERSE_CACHE.read_text())
        if time.time() - cached["fetched_at"] < UNIVERSE_MAX_AGE_S:
            return cached["symbols"]
    try:
        symbols = sorted({s.replace(".", "-") for s in _fetch_sp500() + _fetch_nasdaq100()})
        if len(symbols) < 400:
            raise ValueError(f"universo sospetto: solo {len(symbols)} simboli")
        UNIVERSE_CACHE.write_text(json.dumps({"fetched_at": time.time(), "symbols": symbols}))
        return symbols
    except Exception as exc:
        log.warning("fetch universo azioni fallito: %s", exc)
        if UNIVERSE_CACHE.exists():
            return json.loads(UNIVERSE_CACHE.read_text())["symbols"]
        raise


def daily_history(
    tickers: list[str], period: str = "2y", threads: bool = True, min_bars: int = 220
) -> dict[str, pd.DataFrame]:
    """Download daily in batch. Ritorna {ticker: OHLCV} (solo ticker con dati validi).

    threads=False per i primi download: la cache timezone di yfinance (SQLite)
    va in lock se più thread la inizializzano insieme a freddo.
    """
    out: dict[str, pd.DataFrame] = {}
    chunk_size = 100
    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i : i + chunk_size]
        data = yf.download(
            chunk, period=period, interval="1d", group_by="ticker",
            auto_adjust=True, threads=threads, progress=False,
        )
        if data is None or data.empty:
            continue
        for tkr in chunk:
            try:
                df = data[tkr] if len(chunk) > 1 else data
            except KeyError:
                continue
            df = df.dropna(subset=["Close"])
            df = _drop_unclosed_daily(df)
            if len(df) < min_bars:
                continue
            df = df.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]]
            out[tkr] = df
    return out


def intraday_4h(ticker: str) -> pd.DataFrame:
    """Candele 1h (max 60 giorni su Yahoo) ricampionate a 4h, per i trigger di entrata.

    Le barre sono ancorate alle 9:30 ET (apertura di cassa) e limitate alla
    regular session: il vecchio resample a mezzanotte UTC produceva candele
    4H inesistenti su qualsiasi chart (mescolavano pezzi di sessioni diverse).
    Ritorna solo barre chiuse: la barra 4H in formazione è esclusa, come fa
    il percorso crypto con df4.iloc[:-1].
    """
    df = yf.download(ticker, period="60d", interval="1h", auto_adjust=True, progress=False)
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.lower)

    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    df = df.tz_convert(NY_TZ)
    df = df.between_time("09:30", "15:59")  # solo regular session
    if df.empty:
        return pd.DataFrame()

    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    out = df.resample("4h", offset="9h30min").agg(agg).dropna(subset=["close"])
    if out.empty:
        return out

    # Scarta l'ultima barra se non è ancora chiusa: chiude al più presto tra
    # inizio+4h e la chiusura di sessione delle 16:00 del suo giorno.
    now_ny = pd.Timestamp.now(tz=NY_TZ)
    last_start = out.index[-1]
    bar_end = min(
        last_start + pd.Timedelta(hours=4),
        last_start.normalize() + pd.Timedelta(hours=16),
    )
    if now_ny < bar_end:
        out = out.iloc[:-1]
    return out
