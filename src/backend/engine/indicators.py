"""Indicatori base. Definizioni standard (Wilder per RSI/ATR) — vedi docs/STRATEGIA_SWING.md."""
import numpy as np
import pandas as pd


def ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()


def rsi(close: pd.Series, length: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / length, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / length, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / length, adjust=False).mean()


def bollinger_width(close: pd.Series, length: int = 20, mult: float = 2.0) -> pd.Series:
    mid = close.rolling(length).mean()
    std = close.rolling(length).std()
    return (2 * mult * std) / mid


def rvol(volume: pd.Series, length: int = 20) -> pd.Series:
    """Volume del giorno / media volume dei 20 giorni precedenti (esclude il giorno stesso)."""
    return volume / volume.rolling(length).mean().shift(1)


def adr_pct(df: pd.DataFrame, length: int = 20) -> float:
    rng = (df["high"] / df["low"] - 1.0) * 100
    val = rng.rolling(length).mean().iloc[-1]
    return float(val) if pd.notna(val) else 0.0


def pct_return(close: pd.Series, periods: int) -> float:
    if len(close) <= periods:
        return 0.0
    return float(close.iloc[-1] / close.iloc[-1 - periods] - 1.0)
