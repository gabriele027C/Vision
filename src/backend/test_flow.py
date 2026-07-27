"""Test classificazione OI/CVD e pendenza (FASE 4) — soglie PLAYBOOK_THRESHOLDS."""
import numpy as np
import pandas as pd
import pytest

from config import PLAYBOOK_THRESHOLDS
from engine.flow import (
    build_flow_snapshot,
    classify_cvd,
    classify_oi,
    cvd_slope_normalized,
    oi_deltas_from_hist,
)


def test_classify_oi_thresholds():
    assert classify_oi(0.06) == "up"
    assert classify_oi(0.05) == "up"
    assert classify_oi(0.04) == "flat"
    assert classify_oi(-0.05) == "down"
    assert classify_oi(-0.06) == "down"
    assert classify_oi(-0.20) == "collapse"
    assert classify_oi(-0.25) == "collapse"
    assert classify_oi(None) is None


def test_classify_cvd_thresholds():
    assert classify_cvd(0.03) == "up"
    assert classify_cvd(0.02) == "up"
    assert classify_cvd(0.0) == "flat"
    assert classify_cvd(-0.02) == "down"
    assert classify_cvd(-0.06) == "down_strong"
    assert classify_cvd(-0.1) == "down_strong"


def test_oi_deltas_from_4h_hist():
    # 6 barre = 24h; 18 = 3d. Valori: base 100, +10% in 24h, +20% in 3d
    vals = [100.0] * 12 + [100.0] * 6 + [110.0]
    # length 19: index -1 = 110, -1-6 = 100 → Δ24h=0.1; -1-18 = 100 → Δ3d=0.1
    s = pd.Series(vals)
    d = oi_deltas_from_hist(s, bars_per_day=6)
    assert d["oi_value"] == 110.0
    assert d["oi_delta_24h"] == pytest.approx(0.1)
    assert d["oi_delta_3d"] == pytest.approx(0.1)


def test_cvd_slope_buy_pressure_positive():
    n = PLAYBOOK_THRESHOLDS["cvd"]["slope_bars"]
    vol = np.full(n, 1000.0)
    # taker buy = 80% del volume → delta positivo costante → CVD cresce linearmente
    tbb = vol * 0.8
    slope = cvd_slope_normalized(vol, tbb)
    assert slope is not None and slope > 0
    assert classify_cvd(slope) == "up"


def test_cvd_slope_sell_pressure_strong():
    n = PLAYBOOK_THRESHOLDS["cvd"]["slope_bars"]
    vol = np.full(n, 1000.0)
    tbb = vol * 0.05  # quasi solo sell
    slope = cvd_slope_normalized(vol, tbb)
    assert slope is not None and slope < 0
    assert classify_cvd(slope) in ("down", "down_strong")


def test_build_flow_snapshot_arrows():
    snap = build_flow_snapshot(
        oi_value=1e6,
        oi_delta_24h=0.08,
        oi_delta_3d=0.12,
        cvd_slope=0.2,
        price_delta=0.02,
    )
    assert snap["oi_state"] == "up"
    assert snap["oi_arrow"] == "↑"
    assert snap["cvd_state"] == "up"
    assert snap["cvd_arrow"] == "↑"
    assert snap["price_state"] == "up"
    assert "prezzo↑" in snap["combo_label"]


def test_collapse_priority_over_down():
    assert classify_oi(-0.20) == "collapse"
    assert classify_oi(-0.19) == "down"
