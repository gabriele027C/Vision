"""Rilevamento Setup A (pullback in trend) e Setup B (breakout da compressione).



Implementazione fedele a docs/STRATEGIA_SWING.md §4-§6. Output: dict con livelli

operativi (trigger, stop) da verificare manualmente su TradingView prima dell'ordine.

"""

import pandas as pd



from config import MARKET_PARAMS, MAX_STOP_ATR, RVOL_BREAKOUT

from engine.indicators import atr, bollinger_width, ema, rsi, rvol



SQUEEZE_LOOKBACK = 60

RANGE_BARS = 15  # ~3 settimane di borsa



# Fallback storici (market=None): stessi valori usati prima della Fase 5.

_DEFAULT_PARAMS = {

    "RANGE_BARS": RANGE_BARS,

    "SQUEEZE_LOOKBACK": SQUEEZE_LOOKBACK,

    "RSI_LONG_MIN": 40,

    "RSI_SHORT_MAX": 60,

}





def _market_params(market: str | None) -> dict:

    """Parametri per mercato da MARKET_PARAMS, vecchi default come fallback."""

    if market in MARKET_PARAMS:

        return {**_DEFAULT_PARAMS, **MARKET_PARAMS[market]}

    return _DEFAULT_PARAMS





def _round_px(x: float) -> float:

    return float(f"{x:.6g}")





def setup_a_metrics(df: pd.DataFrame, direction: str, market: str | None = None) -> dict | None:

    """Metriche e flag Setup A — usate da detect_setup_a e diagnostica."""

    if len(df) < 220:

        return None

    p = _market_params(market)

    close, volume = df["close"], df["volume"]

    e20, e50, e200 = ema(close, 20), ema(close, 50), ema(close, 200)

    a = float(atr(df).iloc[-1])

    r = float(rsi(close).iloc[-1])

    last = float(close.iloc[-1])

    vol5 = float(volume.rolling(5).mean().iloc[-1])

    vol20 = float(volume.rolling(20).mean().iloc[-1])

    vol_declining = vol5 < vol20



    if direction == "long":

        aligned = (

            e20.iloc[-1] > e50.iloc[-1] > e200.iloc[-1] and e50.iloc[-1] > e50.iloc[-6]

        )

        in_zone = (e50.iloc[-1] - 0.5 * a) <= last <= (e20.iloc[-1] + 0.25 * a)

        momentum_ok = r > p["RSI_LONG_MIN"]

        swing = float(df["low"].rolling(10).min().iloc[-1])

        stop = swing - 0.5 * a

        trigger = float(df["high"].iloc[-2:].max())

    else:

        aligned = (

            e20.iloc[-1] < e50.iloc[-1] < e200.iloc[-1] and e50.iloc[-1] < e50.iloc[-6]

        )

        in_zone = (e20.iloc[-1] - 0.25 * a) <= last <= (e50.iloc[-1] + 0.5 * a)

        momentum_ok = r < p["RSI_SHORT_MAX"]

        swing = float(df["high"].rolling(10).max().iloc[-1])

        stop = swing + 0.5 * a

        trigger = float(df["low"].iloc[-2:].min())



    stop_dist = abs(trigger - stop)

    stop_geometry_ok = stop_dist <= MAX_STOP_ATR * a



    return {

        "aligned": aligned,

        "in_zone": in_zone,

        "momentum_ok": momentum_ok,

        "vol_declining": vol_declining,

        "stop_geometry_ok": stop_geometry_ok,

        "rsi": r,

        "atr": a,

        "trigger": trigger,

        "stop": stop,

        "stop_dist": stop_dist,

        "vol5": vol5,

        "vol20": vol20,

    }





def setup_b_metrics(df: pd.DataFrame, direction: str, market: str | None = None) -> dict | None:

    """Metriche e flag Setup B — usate da detect_setup_b e diagnostica."""

    if len(df) < 220:

        return None

    p = _market_params(market)

    squeeze_lookback = p["SQUEEZE_LOOKBACK"]

    range_bars = p["RANGE_BARS"]

    close = df["close"]

    e200 = float(ema(close, 200).iloc[-1])

    last = float(close.iloc[-1])

    a = float(atr(df).iloc[-1])



    bbw = bollinger_width(close)

    bbw_last = float(bbw.iloc[-1])

    bbw_thresh = float(bbw.iloc[-squeeze_lookback:].quantile(0.10))

    squeeze = bbw_last <= bbw_thresh



    # Il range di compressione esclude la barra corrente: includerla rendeva
    # impossibile close > rng_high (close <= high), quindi breakout_triggered
    # era sempre False (codice morto). Il breakout è la rottura, da parte della
    # barra corrente, del range delle RANGE_BARS barre precedenti.
    rng_high = float(df["high"].iloc[-range_bars - 1:-1].max())

    rng_low = float(df["low"].iloc[-range_bars - 1:-1].min())



    if direction == "long":

        context_ok = last >= e200

        trigger = rng_high

        stop = max(trigger - a, rng_low)

    else:

        context_ok = last <= e200

        trigger = rng_low

        stop = min(trigger + a, rng_high)



    stop_dist = abs(trigger - stop)

    stop_geometry_ok = stop_dist <= MAX_STOP_ATR * a



    rv_series = rvol(df["volume"])

    rv = float(rv_series.iloc[-1]) if pd.notna(rv_series.iloc[-1]) else 0.0

    triggered = (

        direction == "long" and last > trigger and rv >= RVOL_BREAKOUT

    ) or (

        direction == "short" and last < trigger and rv >= RVOL_BREAKOUT

    )



    return {

        "squeeze": squeeze,

        "context_ok": context_ok,

        "stop_geometry_ok": stop_geometry_ok,

        "breakout_triggered": triggered,

        "bbw_last": bbw_last,

        "bbw_thresh": bbw_thresh,

        "atr": a,

        "trigger": trigger,

        "stop": stop,

        "stop_dist": stop_dist,

        "rvol": rv,

        "e200": e200,

        "last": last,

    }





def detect_setup_a(df: pd.DataFrame, direction: str, market: str | None = None) -> dict | None:

    """Pullback verso EMA20-EMA50 in trend allineato, volume in calo, RSI intatto."""

    m = setup_a_metrics(df, direction, market)

    if m is None:

        return None

    if not (m["aligned"] and m["in_zone"] and m["momentum_ok"] and m["vol_declining"]):

        return None

    if not m["stop_geometry_ok"]:

        return None



    return {

        "setup": "A",

        "direction": direction,

        "entry_trigger": _round_px(m["trigger"]),

        "stop": _round_px(m["stop"]),

        "atr": _round_px(m["atr"]),

        "rsi": round(m["rsi"], 1),

        "note": "Pullback in trend: conferma il trigger sulla candela 4H con volume (TradingView)",

    }





def detect_setup_b(df: pd.DataFrame, direction: str, market: str | None = None) -> dict | None:

    """Compressione di volatilità (squeeze BB / range) + livello di rottura con RVOL>=2."""

    m = setup_b_metrics(df, direction, market)

    if m is None:

        return None

    if not m["squeeze"]:

        return None

    if not m["context_ok"]:

        return None

    if not m["stop_geometry_ok"]:

        return None



    return {

        "setup": "B",

        "direction": direction,

        "entry_trigger": _round_px(m["trigger"]),

        "stop": _round_px(m["stop"]),

        "atr": _round_px(m["atr"]),

        "status_hint": "triggered" if m["breakout_triggered"] else "watch",

        "note": f"Breakout da squeeze: serve chiusura daily oltre il livello con RVOL>={RVOL_BREAKOUT}",

    }





def trigger_status_4h(df_4h: pd.DataFrame, direction: str, trigger: float) -> str:

    """'triggered' | 'near' | 'watch' valutato sulle candele 4H (con conferma volume)."""

    if df_4h.empty or len(df_4h) < 25:

        return "watch"

    last_close = float(df_4h["close"].iloc[-1])

    vol_ok = df_4h["volume"].iloc[-1] > df_4h["volume"].rolling(20).mean().iloc[-1]

    if direction == "long":

        if last_close > trigger and vol_ok:

            return "triggered"

        if last_close >= trigger * 0.99:

            return "near"

    else:

        if last_close < trigger and vol_ok:

            return "triggered"

        if last_close <= trigger * 1.01:

            return "near"

    return "watch"


