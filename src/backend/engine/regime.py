"""Filtro di regime (§2 della strategia): il semaforo che decide long/short/stop."""
import pandas as pd

from config import VIX_HALT
from engine.indicators import ema


def _trend(df: pd.DataFrame) -> str:
    """'up' | 'down' | 'mixed' sul daily: prezzo vs EMA200 + pendenza EMA50."""
    close = df["close"]
    e50 = ema(close, 50)
    e200 = ema(close, 200)
    last = close.iloc[-1]
    slope_up = e50.iloc[-1] > e50.iloc[-6]
    if last > e200.iloc[-1] and slope_up:
        return "up"
    if last < e200.iloc[-1] and not slope_up:
        return "down"
    return "mixed"


def stock_regime(spy: pd.DataFrame, qqq: pd.DataFrame, vix_last: float | None) -> dict:
    t_spy, t_qqq = _trend(spy), _trend(qqq)
    if vix_last is not None and vix_last > VIX_HALT:
        mode = "halt"
    elif t_spy == "up" and t_qqq == "up":
        mode = "long"
    elif t_spy == "down" and t_qqq == "down":
        mode = "short"
    else:
        mode = "mixed"
    return {
        "market": "stocks",
        "mode": mode,
        "long_allowed": mode in ("long", "mixed"),
        "short_allowed": mode in ("short", "mixed"),
        "half_size": mode == "mixed",
        "detail": {"SPY": t_spy, "QQQ": t_qqq, "VIX": vix_last},
    }


def crypto_regime(btc: pd.DataFrame) -> dict:
    close = btc["close"]
    e50, e200 = ema(close, 50), ema(close, 200)
    last = close.iloc[-1]
    if last > e200.iloc[-1] and last > e50.iloc[-1]:
        mode = "long"
    elif last < e200.iloc[-1] and last < e50.iloc[-1]:
        mode = "short"
    else:
        mode = "mixed"  # solo BTC/ETH, size dimezzata
    return {
        "market": "crypto",
        "mode": mode,
        "long_allowed": mode in ("long", "mixed"),
        "short_allowed": mode in ("short", "mixed"),
        "half_size": mode == "mixed",
        "detail": {
            "BTC_vs_EMA200": "above" if last > e200.iloc[-1] else "below",
            "BTC_vs_EMA50": "above" if last > e50.iloc[-1] else "below",
        },
    }
