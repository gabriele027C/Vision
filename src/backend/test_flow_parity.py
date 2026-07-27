"""Parità Py↔TS su dati sintetici: flag e classificazioni OI/CVD (FASE 4).

Esegue i calcoli Python e stampa un vettore di asserzioni che il motore TS
deve replicare (stessi input → stessi stati). Usato anche come test pytest.
"""
from __future__ import annotations

import json

import numpy as np

from engine.flow import (
    build_flow_snapshot,
    classify_cvd,
    classify_oi,
    cvd_slope_normalized,
    oi_deltas_from_hist,
)
import pandas as pd


# Casi di soglia (identici a vision-mobile/src/engine/flow.ts)
OI_CASES = [
    (0.06, "up"),
    (0.05, "up"),
    (0.049, "flat"),
    (-0.05, "down"),
    (-0.19, "down"),
    (-0.20, "collapse"),
    (-0.25, "collapse"),
]

CVD_CASES = [
    (0.03, "up"),
    (0.02, "up"),
    (0.0, "flat"),
    (-0.02, "down"),
    (-0.05, "down"),
    (-0.06, "down_strong"),
]


def parity_payload() -> dict:
    oi_series = pd.Series([100.0] * 18 + [112.0])
    deltas = oi_deltas_from_hist(oi_series, bars_per_day=6)

    n = 20
    vol = np.full(n, 1000.0)
    tbb_up = vol * 0.75
    tbb_down = vol * 0.2
    slope_up = cvd_slope_normalized(vol, tbb_up)
    slope_down = cvd_slope_normalized(vol, tbb_down)

    snap = build_flow_snapshot(
        oi_value=deltas["oi_value"],
        oi_delta_24h=deltas["oi_delta_24h"],
        oi_delta_3d=deltas["oi_delta_3d"],
        cvd_slope=slope_up,
        price_delta=0.02,
    )

    return {
        "oi_cases": [{"delta": d, "state": classify_oi(d)} for d, _ in OI_CASES],
        "cvd_cases": [{"slope": s, "state": classify_cvd(s)} for s, _ in CVD_CASES],
        "oi_deltas": {
            "oi_value": deltas["oi_value"],
            "oi_delta_24h": deltas["oi_delta_24h"],
            "oi_delta_3d": deltas["oi_delta_3d"],
            "oi_state": classify_oi(deltas["oi_delta_24h"]),
        },
        "cvd_slopes": {
            "up": slope_up,
            "up_state": classify_cvd(slope_up),
            "down": slope_down,
            "down_state": classify_cvd(slope_down),
        },
        "snap": {
            "oi_state": snap["oi_state"],
            "cvd_state": snap["cvd_state"],
            "price_state": snap["price_state"],
            "oi_arrow": snap["oi_arrow"],
            "cvd_arrow": snap["cvd_arrow"],
            "combo_key": snap["combo_key"],
        },
    }


def test_parity_vectors_stable():
    p = parity_payload()
    for case, expected in zip(p["oi_cases"], OI_CASES):
        assert case["state"] == expected[1]
    for case, expected in zip(p["cvd_cases"], CVD_CASES):
        assert case["state"] == expected[1]
    assert p["oi_deltas"]["oi_state"] == "up"
    assert p["cvd_slopes"]["up_state"] == "up"
    assert p["snap"]["oi_arrow"] == "↑"


if __name__ == "__main__":
    print(json.dumps(parity_payload(), indent=2, default=float))
