"""OI + CVD: classificazione descrittiva (FASE 4).

Nessun claim predittivo. Soglie in PLAYBOOK_THRESHOLDS (ipotesi non validate).
CVD: delta = taker_buy − (volume − taker_buy) = 2·tbb − volume; cumulato; slope
= regressione lineare su N barre, normalizzata sul volume medio.
"""
from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd

from config import PLAYBOOK_THRESHOLDS

OiState = Literal["up", "down", "flat", "collapse"]
CvdState = Literal["up", "down", "flat", "down_strong"]
PriceState = Literal["up", "down", "flat"]

STATE_ARROW = {
    "up": "↑",
    "down": "↓",
    "flat": "→",
    "collapse": "↓↓",
    "down_strong": "↓↓",
}


def classify_oi(delta_24h: float | None) -> OiState | None:
    """Classifica Δ OI 24h (frazione). None se input mancante."""
    if delta_24h is None or not np.isfinite(delta_24h):
        return None
    thr = PLAYBOOK_THRESHOLDS["oi"]
    if delta_24h <= thr["collapse_pct_24h"]:
        return "collapse"
    if delta_24h >= thr["up_pct_24h"]:
        return "up"
    if delta_24h <= thr["down_pct_24h"]:
        return "down"
    return "flat"


def classify_cvd(slope_norm: float | None) -> CvdState | None:
    """Classifica pendenza CVD normalizzata sul volume medio."""
    if slope_norm is None or not np.isfinite(slope_norm):
        return None
    thr = PLAYBOOK_THRESHOLDS["cvd"]
    if slope_norm <= thr["down_strong"]:
        return "down_strong"
    if slope_norm >= thr["up"]:
        return "up"
    if slope_norm <= thr["down"]:
        return "down"
    return "flat"


def classify_price(delta_pct: float | None, flat_band: float | None = None) -> PriceState | None:
    """Direzione prezzo descrittiva (es. close vs N barre fa)."""
    if delta_pct is None or not np.isfinite(delta_pct):
        return None
    band = PLAYBOOK_THRESHOLDS["prezzo"]["flat_band"] if flat_band is None else flat_band
    if delta_pct >= band:
        return "up"
    if delta_pct <= -band:
        return "down"
    return "flat"


def oi_deltas_from_hist(oi_series: pd.Series, bars_per_day: int = 6) -> dict:
    """Da serie OI (period 4h → 6 barre/giorno): valore, Δ24h, Δ3d (frazioni)."""
    if oi_series is None or len(oi_series) < 2:
        return {"oi_value": None, "oi_delta_24h": None, "oi_delta_3d": None}
    last = float(oi_series.iloc[-1])
    out: dict = {"oi_value": last, "oi_delta_24h": None, "oi_delta_3d": None}
    if last <= 0:
        return out
    i24 = bars_per_day  # 6×4h = 24h
    i3d = bars_per_day * 3
    if len(oi_series) > i24:
        prev = float(oi_series.iloc[-1 - i24])
        if prev > 0:
            out["oi_delta_24h"] = (last - prev) / prev
    if len(oi_series) > i3d:
        prev = float(oi_series.iloc[-1 - i3d])
        if prev > 0:
            out["oi_delta_3d"] = (last - prev) / prev
    return out


def bar_delta(volume: float, taker_buy: float) -> float:
    """Delta aggressori: buy − sell = 2·tbb − volume."""
    return 2.0 * taker_buy - volume


def cvd_series(volume: np.ndarray | pd.Series, taker_buy: np.ndarray | pd.Series) -> np.ndarray:
    vol = np.asarray(volume, dtype=float)
    tbb = np.asarray(taker_buy, dtype=float)
    return np.cumsum(2.0 * tbb - vol)


def cvd_slope_normalized(
    volume: np.ndarray | pd.Series,
    taker_buy: np.ndarray | pd.Series,
    *,
    bars: int | None = None,
) -> float | None:
    """Pendenza regressione su `bars` barre, / volume medio. None se dati insufficienti."""
    n = PLAYBOOK_THRESHOLDS["cvd"]["slope_bars"] if bars is None else bars
    vol = np.asarray(volume, dtype=float)
    tbb = np.asarray(taker_buy, dtype=float)
    if len(vol) < n or len(tbb) < n:
        return None
    v = vol[-n:]
    t = tbb[-n:]
    cvd = np.cumsum(2.0 * t - v)
    mean_vol = float(np.mean(v))
    if not (mean_vol > 0):
        return None
    x = np.arange(n, dtype=float)
    # slope OLS: cov(x,y)/var(x)
    x_mean = x.mean()
    y_mean = cvd.mean()
    var_x = float(np.sum((x - x_mean) ** 2))
    if var_x <= 0:
        return None
    slope = float(np.sum((x - x_mean) * (cvd - y_mean)) / var_x)
    return slope / mean_vol


def price_delta_pct(close: pd.Series | np.ndarray, lookback: int = 6) -> float | None:
    """Δ% close vs lookback barre fa (default 6 ≈ 1g su 4h)."""
    c = np.asarray(close, dtype=float)
    if len(c) <= lookback:
        return None
    prev = c[-1 - lookback]
    if not (prev > 0):
        return None
    return float((c[-1] - prev) / prev)


def describe_combo(
    price: PriceState | None,
    oi: OiState | None,
    cvd: CvdState | None,
) -> dict:
    """Classificazione descrittiva prezzo/OI/CVD (non è matching playbook)."""
    key = f"price_{price or 'na'}|oi_{oi or 'na'}|cvd_{cvd or 'na'}"
    if price is None and oi is None and cvd is None:
        return {
            "combo_key": key,
            "label": "flusso non disponibile",
            "message": "OI/CVD non calcolabili per questo asset",
        }

    parts = []
    if price == "up":
        parts.append("prezzo↑")
    elif price == "down":
        parts.append("prezzo↓")
    elif price == "flat":
        parts.append("prezzo→")

    if oi == "up":
        parts.append("OI↑")
    elif oi == "down":
        parts.append("OI↓")
    elif oi == "collapse":
        parts.append("OI collapse")
    elif oi == "flat":
        parts.append("OI→")

    if cvd == "up":
        parts.append("CVD↑")
    elif cvd == "down":
        parts.append("CVD↓")
    elif cvd == "down_strong":
        parts.append("CVD↓↓")
    elif cvd == "flat":
        parts.append("CVD→")

    label = " + ".join(parts) if parts else "flusso parziale"

    # Lettura descrittiva (condizionale, non predittiva)
    if price == "up" and oi == "up" and cvd == "up":
        reading = "Partecipazione in aumento col prezzo (nuovi aggressori in acquisto) — descrittivo."
    elif price == "up" and oi == "down":
        reading = "Prezzo↑ con OI↓: tipico short covering — base potenzialmente fragile."
    elif price == "up" and (oi in ("flat", None)) and cvd in ("flat", "down", "down_strong", None):
        reading = "Prezzo↑ senza conferma aggressori — trend sottile o esausto."
    elif oi == "collapse":
        reading = "OI in collasso (−20%+ /24h): deleveraging / liquidazioni in corso."
    elif cvd == "down_strong" and price == "up":
        reading = "Prezzo↑ ma CVD fortemente negativo: possibile distribuzione."
    elif price == "down" and oi == "up" and cvd in ("down", "down_strong"):
        reading = "Prezzo↓ + OI↑ + CVD↓: nuovi short / pressione in vendita."
    else:
        reading = "Combinazione mista — confronta col grafico; nessuna inferenza automatica."

    return {"combo_key": key, "label": label, "message": reading}


def build_flow_snapshot(
    *,
    oi_value: float | None = None,
    oi_delta_24h: float | None = None,
    oi_delta_3d: float | None = None,
    cvd_slope: float | None = None,
    price_delta: float | None = None,
) -> dict:
    """Snapshot completo per diagnostica + sintesi watchlist/journal."""
    oi_state = classify_oi(oi_delta_24h)
    cvd_state = classify_cvd(cvd_slope)
    price_state = classify_price(price_delta)
    combo = describe_combo(price_state, oi_state, cvd_state)
    return {
        "oi_value": oi_value,
        "oi_delta_24h": round(oi_delta_24h, 6) if oi_delta_24h is not None else None,
        "oi_delta_3d": round(oi_delta_3d, 6) if oi_delta_3d is not None else None,
        "oi_state": oi_state,
        "oi_arrow": STATE_ARROW.get(oi_state) if oi_state else None,
        "cvd_slope": round(cvd_slope, 6) if cvd_slope is not None else None,
        "cvd_state": cvd_state,
        "cvd_arrow": STATE_ARROW.get(cvd_state) if cvd_state else None,
        "price_state": price_state,
        "combo_key": combo["combo_key"],
        "combo_label": combo["label"],
        "combo_message": combo["message"],
    }


def flow_filters_from_snapshot(snap: dict) -> list[dict]:
    """FilterResult-like list per la sezione diagnostica flusso."""
    out = []

    def fr(fid, label, status, value, message):
        out.append({
            "id": fid,
            "label": label,
            "status": status,
            "value": value,
            "threshold": None,
            "message": message,
        })

    oi_v = snap.get("oi_value")
    d24 = snap.get("oi_delta_24h")
    d3d = snap.get("oi_delta_3d")
    oi_st = snap.get("oi_state")
    if oi_v is None and d24 is None:
        fr("oi", "Open interest", "skip", None, "OI non disponibile")
    else:
        d24_pct = f"{d24 * 100:+.2f}%" if d24 is not None else "n/d"
        d3d_pct = f"{d3d * 100:+.2f}%" if d3d is not None else "n/d"
        fr(
            "oi",
            f"OI {snap.get('oi_arrow') or ''}".strip(),
            "warn" if oi_st in ("collapse", "down") else "pass",
            round(oi_v, 2) if oi_v is not None else None,
            f"OI={oi_v:.4g} · Δ24h {d24_pct} ({oi_st}) · Δ3d {d3d_pct}"
            if oi_v is not None
            else f"Δ24h {d24_pct} ({oi_st}) · Δ3d {d3d_pct}",
        )

    slope = snap.get("cvd_slope")
    cvd_st = snap.get("cvd_state")
    if slope is None:
        fr("cvd", "CVD slope", "skip", None, "CVD non calcolabile")
    else:
        fr(
            "cvd",
            f"CVD {snap.get('cvd_arrow') or ''}".strip(),
            "warn" if cvd_st in ("down", "down_strong") else "pass",
            slope,
            f"pendenza norm. {slope:+.4f} → {cvd_st} (ipotesi PLAYBOOK_THRESHOLDS)",
        )

    fr(
        "flow_combo",
        "Combinazione prezzo/OI/CVD",
        "pass",
        snap.get("combo_label"),
        snap.get("combo_message") or "",
    )
    return out


def attach_flow_summary(row: dict, snap: dict) -> None:
    """Sintesi watchlist: frecce + campi journal-ready."""
    row["oi_state"] = snap.get("oi_state")
    row["oi_arrow"] = snap.get("oi_arrow")
    row["oi_value"] = snap.get("oi_value")
    row["oi_delta_24h"] = snap.get("oi_delta_24h")
    row["oi_delta_3d"] = snap.get("oi_delta_3d")
    row["cvd_state"] = snap.get("cvd_state")
    row["cvd_arrow"] = snap.get("cvd_arrow")
    row["cvd_slope"] = snap.get("cvd_slope")
    row["flow_combo_label"] = snap.get("combo_label")


__all__ = [
    "STATE_ARROW",
    "classify_oi",
    "classify_cvd",
    "classify_price",
    "oi_deltas_from_hist",
    "bar_delta",
    "cvd_series",
    "cvd_slope_normalized",
    "price_delta_pct",
    "describe_combo",
    "build_flow_snapshot",
    "flow_filters_from_snapshot",
    "attach_flow_summary",
]
