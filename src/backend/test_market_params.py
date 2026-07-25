"""Unit test Fase 5: MARKET_PARAMS per mercato in setups — nessuna rete."""
from __future__ import annotations

import numpy as np
import pandas as pd

from config import MARKET_PARAMS
from engine.diagnostics import diagnose_setup_a, diagnose_setup_b
from engine.setups import (
    RANGE_BARS,
    SQUEEZE_LOOKBACK,
    _market_params,
    detect_setup_a,
    detect_setup_b,
    setup_a_metrics,
    setup_b_metrics,
)
from test_diagnostics import make_ohlcv


def make_rsi_df(gain: float, loss: float, n: int = 250, base: float = 500.0) -> pd.DataFrame:
    """Serie con delta alternati +gain/-loss: RSI Wilder → 100*gain/(gain+loss)."""
    deltas = np.tile([gain, -loss], n // 2 + 1)[:n]
    close = base + np.cumsum(deltas)
    idx = pd.date_range("2020-01-01", periods=n, freq="D", tz="UTC")
    return pd.DataFrame(
        {
            "open": close - deltas,
            "high": close + 0.5,
            "low": close - 0.5,
            "close": close,
            "volume": np.full(n, 1e6),
        },
        index=idx,
    )


# ---------- Risoluzione parametri ----------


def test_market_params_resolution():
    crypto = _market_params("crypto")
    stocks = _market_params("stocks")
    default = _market_params(None)
    assert crypto["RANGE_BARS"] == 21
    assert crypto["SQUEEZE_LOOKBACK"] == 84
    assert crypto["RSI_LONG_MIN"] == 35
    assert crypto["RSI_SHORT_MAX"] == 65
    assert stocks["RANGE_BARS"] == 15
    assert stocks["SQUEEZE_LOOKBACK"] == 60
    assert stocks["RSI_LONG_MIN"] == 40
    assert stocks["RSI_SHORT_MAX"] == 60
    # market=None → vecchi default pre-Fase 5
    assert default["RANGE_BARS"] == RANGE_BARS == 15
    assert default["SQUEEZE_LOOKBACK"] == SQUEEZE_LOOKBACK == 60
    assert default["RSI_LONG_MIN"] == 40
    assert default["RSI_SHORT_MAX"] == 60
    assert set(MARKET_PARAMS.keys()) == {"crypto", "stocks"}


def test_unknown_market_falls_back_to_default():
    assert _market_params("forex") == _market_params(None)


# ---------- Soglie RSI Setup A ----------


def test_rsi_long_threshold_crypto_more_permissive():
    # RSI ≈ 100*0.587/1.587 ≈ 37: tra la soglia crypto (35) e quella default (40)
    df = make_rsi_df(gain=0.587, loss=1.0)
    m_def = setup_a_metrics(df, "long")
    m_cry = setup_a_metrics(df, "long", market="crypto")
    m_stk = setup_a_metrics(df, "long", market="stocks")
    assert 35 < m_def["rsi"] < 40
    assert m_def["momentum_ok"] is False   # default: serve >40
    assert m_cry["momentum_ok"] is True    # crypto: serve >35
    assert m_stk["momentum_ok"] is False   # stocks: come default


def test_rsi_short_threshold_crypto_more_permissive():
    # RSI ≈ 100*1.0/1.587 ≈ 63: tra la soglia default (60) e quella crypto (65)
    df = make_rsi_df(gain=1.0, loss=0.587)
    m_def = setup_a_metrics(df, "short")
    m_cry = setup_a_metrics(df, "short", market="crypto")
    assert 60 < m_def["rsi"] < 65
    assert m_def["momentum_ok"] is False   # default: serve <60
    assert m_cry["momentum_ok"] is True    # crypto: serve <65


# ---------- RANGE_BARS Setup B ----------


def test_range_bars_crypto_uses_wider_window():
    n = 250
    idx = pd.date_range("2020-01-01", periods=n, freq="D", tz="UTC")
    df = pd.DataFrame(
        {
            "open": np.full(n, 100.0),
            "high": np.full(n, 101.0),
            "low": np.full(n, 99.0),
            "close": np.full(n, 100.0),
            "volume": np.full(n, 1e6),
        },
        index=idx,
    )
    # Spike a -18: dentro la finestra crypto (21 barre precedenti), fuori da quella default (15)
    df.iloc[-18, df.columns.get_loc("high")] = 120.0

    m_def = setup_b_metrics(df, "long")
    m_cry = setup_b_metrics(df, "long", market="crypto")
    assert m_def["trigger"] == 101.0
    assert m_cry["trigger"] == 120.0


# ---------- Coerenza detect ⟷ diagnose con market ----------


def test_detect_diagnose_coherence_with_market():
    fixtures = [
        make_ohlcv(daily_return=0.003, noise=0.001),
        make_ohlcv(daily_return=-0.003, noise=0.001),
        make_ohlcv(daily_return=0.0, noise=0.02),
    ]
    for df in fixtures:
        for direction in ("long", "short"):
            for market in ("crypto", "stocks", None):
                da = diagnose_setup_a(df, direction, market)
                assert da["eligible"] == (detect_setup_a(df, direction, market) is not None)
                db = diagnose_setup_b(df, direction, market)
                assert db["eligible"] == (detect_setup_b(df, direction, market) is not None)


def test_diagnose_setup_a_reports_market_threshold():
    df = make_rsi_df(gain=0.587, loss=1.0)
    d = diagnose_setup_a(df, "long", "crypto")
    rsi_f = next(f for f in d["filters"] if f["id"] == "setup_a_momentum")
    assert rsi_f["threshold"] == 35
