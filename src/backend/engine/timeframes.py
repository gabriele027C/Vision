"""Detection multi-timeframe gerarchica (FASE 3).

Architettura:
- D e 4H determinano l'ingresso in watchlist (situazioni operative long).
- 1H e 15m si attivano SOLO per asset già in watchlist: informazione di timing
  ("compressione 15m sopra il livello daily"). Nessun alert autonomo dai TF bassi;
  al più una notifica di timing con rate-limit 1/asset/4h.

Anti-lookahead (come daily): solo candele chiuse; range che esclude la barra
corrente; invalidazione = distanza in ATR-del-TF (moltiplicatore crescente
sui TF bassi — ipotesi descrittiva, non stop di un sistema validato).
"""
from __future__ import annotations

import time

import pandas as pd

from config import (
    TF_PARAMS,
    TIMING_ALERT_COOLDOWN_S,
    TIMING_TFS,
    WATCHLIST_ENTRY_TFS,
)
from engine.indicators import atr, bollinger_width, ema, rvol
from engine.setups import _round_px


def tf_params(timeframe: str) -> dict:
    """Parametri per timeframe. KeyError se TF sconosciuto."""
    return TF_PARAMS[timeframe]


def compression_metrics(
    df: pd.DataFrame,
    direction: str = "long",
    timeframe: str = "D",
) -> dict | None:
    """Compressione (squeeze BB) + livello di rottura/invalidazione sul TF dato.

    Stessa semantica anti-lookahead di setup_b_metrics:
    - range sulle RANGE_BARS barre PRIMA della corrente;
    - quantile squeeze sulle barre PRIMA della corrente;
    - solo barre chiuse (il chiamante passa già df senza barra in formazione).
    """
    p = tf_params(timeframe)
    min_bars = p["MIN_BARS"]
    if len(df) < min_bars:
        return None

    range_bars = p["RANGE_BARS"]
    squeeze_lookback = p["SQUEEZE_LOOKBACK"]
    inv_mult = p["INVALIDATION_ATR"]

    close = df["close"]
    last = float(close.iloc[-1])
    e200 = float(ema(close, min(200, len(close) - 1)).iloc[-1])
    a = float(atr(df).iloc[-1])
    if not (a > 0):
        return None

    bbw = bollinger_width(close)
    bbw_last = float(bbw.iloc[-1])
    bbw_thresh = float(bbw.iloc[-squeeze_lookback - 1:-1].quantile(0.10))
    squeeze = bbw_last <= bbw_thresh

    rng_high = float(df["high"].iloc[-range_bars - 1:-1].max())
    rng_low = float(df["low"].iloc[-range_bars - 1:-1].min())

    if direction == "long":
        context_ok = last >= e200
        trigger = rng_high
        # Invalidazione descrittiva: distanza inv_mult*ATR sotto il trigger.
        # Più ampia sui TF bassi (rumore/costi). Non è uno stop validato.
        stop = trigger - inv_mult * a
    else:
        context_ok = last <= e200
        trigger = rng_low
        stop = trigger + inv_mult * a

    stop_dist = abs(trigger - stop)
    rv_series = rvol(df["volume"])
    rv = float(rv_series.iloc[-1]) if pd.notna(rv_series.iloc[-1]) else 0.0

    return {
        "timeframe": timeframe,
        "squeeze": squeeze,
        "context_ok": context_ok,
        "bbw_last": bbw_last,
        "bbw_thresh": bbw_thresh,
        "atr": a,
        "trigger": trigger,
        "stop": stop,
        "stop_dist": stop_dist,
        "invalidation_atr_mult": inv_mult,
        "rvol": rv,
        "e200": e200,
        "last": last,
        "rng_high": rng_high,
        "rng_low": rng_low,
    }


def detect_compression(
    df: pd.DataFrame,
    direction: str = "long",
    timeframe: str = "D",
) -> dict | None:
    """Ritorna situazione di compressione se squeeze+context, con livelli arrotondati."""
    m = compression_metrics(df, direction, timeframe)
    if m is None or not m["squeeze"] or not m["context_ok"]:
        return None
    return {
        "setup": "B",
        "timeframe": timeframe,
        "direction": direction,
        "entry_trigger": _round_px(m["trigger"]),
        "stop": _round_px(m["stop"]),
        "atr": _round_px(m["atr"]),
        "invalidation_atr_mult": m["invalidation_atr_mult"],
        "rvol": round(m["rvol"], 2),
        "note": (
            f"Compressione {timeframe}: livello di rottura {_round_px(m['trigger'])}, "
            f"invalidazione {_round_px(m['stop'])} ({m['invalidation_atr_mult']}×ATR {timeframe})"
        ),
    }


def closed_klines(df: pd.DataFrame) -> pd.DataFrame:
    """Esclude l'ultima barra (in formazione)."""
    if df is None or df.empty:
        return pd.DataFrame()
    return df.iloc[:-1] if len(df) > 1 else df.iloc[0:0]


class TimingAlertGate:
    """Rate-limit: al massimo 1 notifica timing per asset ogni TIMING_ALERT_COOLDOWN_S."""

    def __init__(self, cooldown_s: float = TIMING_ALERT_COOLDOWN_S):
        self.cooldown_s = cooldown_s
        self._last: dict[str, float] = {}

    def allow(self, symbol: str, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        prev = self._last.get(symbol)
        if prev is not None and (now - prev) < self.cooldown_s:
            return False
        self._last[symbol] = now
        return True


def attach_timing_to_row(
    row: dict,
    lower_tfs: dict[str, pd.DataFrame],
    *,
    direction: str = "long",
) -> list[dict]:
    """Rileva compressioni 1H/15m per un asset già in watchlist. Solo info timing."""
    found: list[dict] = []
    for tf in TIMING_TFS:
        df = lower_tfs.get(tf)
        if df is None or df.empty:
            continue
        hist = closed_klines(df)
        det = detect_compression(hist, direction, tf)
        if det is None:
            continue
        # Timing utile solo se compressione sopra (long) il livello daily di rottura
        daily_level = row.get("entry_trigger")
        if daily_level is not None and direction == "long":
            last = float(hist["close"].iloc[-1])
            if last < float(daily_level):
                det = {
                    **det,
                    "note": det["note"] + " — sotto il livello daily (non timing long)",
                    "aligned_with_daily": False,
                }
            else:
                det = {**det, "aligned_with_daily": True}
        found.append(det)
    return found


__all__ = [
    "TF_PARAMS",
    "WATCHLIST_ENTRY_TFS",
    "TIMING_TFS",
    "tf_params",
    "compression_metrics",
    "detect_compression",
    "closed_klines",
    "TimingAlertGate",
    "attach_timing_to_row",
]
