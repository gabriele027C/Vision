"""Helpers per costruire lo snapshot flusso OI/CVD da REST Binance."""
from __future__ import annotations

import logging

from data import binance_client
from engine.flow import (
    attach_flow_summary,
    build_flow_snapshot,
    cvd_slope_normalized,
    flow_filters_from_snapshot,
    oi_deltas_from_hist,
    price_delta_pct,
)
from engine.timeframes import closed_klines

log = logging.getLogger(__name__)


def fetch_flow_snapshot(symbol: str, *, interval: str = "4h") -> dict:
    """Scarica OI hist 4h + klines futures; costruisce snapshot classificato."""
    oi = binance_client.open_interest_hist(symbol, period="4h", limit=30)
    # Escludi punto in formazione se l'ultima barra OI è troppo recente? Hist è già chiuso a period.
    deltas = oi_deltas_from_hist(oi, bars_per_day=6)

    fut = binance_client.futures_klines(symbol, interval=interval, limit=100)
    hist = closed_klines(fut) if not fut.empty else fut
    slope = None
    px_delta = None
    if not hist.empty and "tbb" in hist.columns:
        slope = cvd_slope_normalized(hist["volume"].values, hist["tbb"].values)
        px_delta = price_delta_pct(hist["close"], lookback=6)

    return build_flow_snapshot(
        oi_value=deltas["oi_value"],
        oi_delta_24h=deltas["oi_delta_24h"],
        oi_delta_3d=deltas["oi_delta_3d"],
        cvd_slope=slope,
        price_delta=px_delta,
    )


def enrich_row_with_flow(row: dict) -> dict:
    """Allega sintesi flusso a una riga watchlist crypto. In caso di errore lascia vuoto."""
    try:
        snap = fetch_flow_snapshot(row["symbol"])
        attach_flow_summary(row, snap)
        row["_flow_snap"] = snap  # usato dalla diagnostica; non serializzare in API se pesante
    except Exception as exc:
        log.warning("flow %s fallito: %s", row.get("symbol"), exc)
    return row


def diagnostics_flow_payload(symbol: str, snap: dict | None = None) -> dict:
    """Sezione diagnostica flusso: filters + snapshot numerico."""
    snap = snap or fetch_flow_snapshot(symbol)
    return {
        "flow": snap,
        "flow_filters": flow_filters_from_snapshot(snap),
    }


__all__ = [
    "fetch_flow_snapshot",
    "enrich_row_with_flow",
    "diagnostics_flow_payload",
]
