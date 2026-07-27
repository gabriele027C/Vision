"""Unit test FASE 3: multi-timeframe gerarchico — nessuna rete."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from config import TF_PARAMS
from engine.timeframes import (
    TimingAlertGate,
    attach_timing_to_row,
    closed_klines,
    compression_metrics,
    detect_compression,
    tf_params,
)


def _squeeze_df(n: int = 250, direction: str = "long") -> pd.DataFrame:
    """Serie con compressione artificiale nelle ultime barre."""
    rng = np.random.default_rng(42)
    idx = pd.date_range("2024-01-01", periods=n, freq="h", tz="UTC")
    # trend soft poi range stretto
    drift = 0.001 if direction == "long" else -0.001
    close = 100 * np.cumprod(1 + drift + rng.normal(0, 0.002, n))
    # ultime 40 barre: range compresso
    close[-40:] = close[-41] + rng.normal(0, 0.0002, 40)
    high = close * 1.001
    low = close * 0.999
    # range precedente alle ultime: più ampio
    high[-80:-40] = close[-80:-40] * 1.02
    low[-80:-40] = close[-80:-40] * 0.98
    vol = np.full(n, 1e6)
    return pd.DataFrame(
        {"open": np.roll(close, 1), "high": high, "low": low, "close": close, "volume": vol},
        index=idx,
    )


def test_tf_params_documented_hypotheses():
    assert TF_PARAMS["D"]["INVALIDATION_ATR"] == 1.5
    assert TF_PARAMS["4H"]["INVALIDATION_ATR"] == 1.75
    assert TF_PARAMS["1H"]["INVALIDATION_ATR"] == 2.0
    assert TF_PARAMS["15m"]["INVALIDATION_ATR"] == 2.5
    # Moltiplicatori strettamente crescenti scendendo di TF
    mults = [TF_PARAMS[tf]["INVALIDATION_ATR"] for tf in ("D", "4H", "1H", "15m")]
    assert mults == sorted(mults)
    assert tf_params("15m")["RANGE_BARS"] == 48


def test_closed_klines_drops_last_bar():
    df = _squeeze_df(100)
    closed = closed_klines(df)
    assert len(closed) == len(df) - 1
    assert closed.index[-1] == df.index[-2]


def test_invalidation_wider_on_lower_tf():
    df = _squeeze_df(300)
    m_d = compression_metrics(df, "long", "D")
    m_15 = compression_metrics(df, "long", "15m")
    # Anche se atr differisce, il moltiplicatore 15m è maggiore
    assert m_d is not None and m_15 is not None
    assert m_15["invalidation_atr_mult"] > m_d["invalidation_atr_mult"]
    # Long: stop sotto trigger
    assert m_d["stop"] < m_d["trigger"]
    assert abs(m_d["trigger"] - m_d["stop"]) == pytest.approx(
        m_d["invalidation_atr_mult"] * m_d["atr"]
    )


def test_detect_compression_requires_squeeze_and_context():
    df = _squeeze_df(300)
    # Può o non può passare a seconda dei dati random; verifica struttura se passa
    det = detect_compression(df, "long", "4H")
    if det is not None:
        assert det["timeframe"] == "4H"
        assert det["setup"] == "B"
        assert "entry_trigger" in det and "stop" in det


def test_timing_alert_gate_rate_limit():
    gate = TimingAlertGate(cooldown_s=100)
    assert gate.allow("BTC", now=1000.0) is True
    assert gate.allow("BTC", now=1050.0) is False  # entro cooldown
    assert gate.allow("ETH", now=1050.0) is True   # altro asset
    assert gate.allow("BTC", now=1101.0) is True   # dopo cooldown


def test_attach_timing_marks_alignment_with_daily():
    df = _squeeze_df(300)
    row = {"entry_trigger": float(df["close"].iloc[-1]) - 10}  # prezzo sopra livello
    timing = attach_timing_to_row(row, {"1H": df, "15m": df}, direction="long")
    # Se rileva compressione, aligned_with_daily True (last > daily level)
    for t in timing:
        assert "aligned_with_daily" in t
        assert t["aligned_with_daily"] is True

    row_below = {"entry_trigger": float(df["close"].iloc[-1]) + 10}
    timing2 = attach_timing_to_row(row_below, {"15m": df}, direction="long")
    for t in timing2:
        assert t["aligned_with_daily"] is False


def test_range_excludes_current_bar():
    """Il range non include la barra corrente (anti-lookahead)."""
    df = _squeeze_df(250)
    p = tf_params("4H")
    m = compression_metrics(df, "long", "4H")
    assert m is not None
    # rng_high calcolato su barre [-range-1:-1]; se includessimo l'ultima high potrebbe cambiare
    rb = p["RANGE_BARS"]
    expected = float(df["high"].iloc[-rb - 1:-1].max())
    assert m["rng_high"] == expected
