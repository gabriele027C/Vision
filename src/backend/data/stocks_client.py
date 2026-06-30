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

import httpx
import pandas as pd
import yfinance as yf

from config import CACHE_DIR

log = logging.getLogger(__name__)

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
            if len(df) < min_bars:
                continue
            df = df.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]]
            out[tkr] = df
    return out


def intraday_4h(ticker: str) -> pd.DataFrame:
    """Candele 1h (max 60 giorni su Yahoo) ricampionate a 4h, per i trigger di entrata."""
    df = yf.download(ticker, period="60d", interval="1h", auto_adjust=True, progress=False)
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.lower)
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    return df.resample("4h").agg(agg).dropna(subset=["close"])
