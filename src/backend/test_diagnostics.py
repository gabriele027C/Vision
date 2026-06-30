"""Unit test diagnostica filtri — nessuna rete (default CI)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from config import MAX_STOP_ATR, RS_BOTTOM_PERCENTILE, RS_TOP_PERCENTILE, VIX_HALT
from engine import regime as regime_mod
from engine.diagnostics import (
    diagnose_asset,
    diagnose_regime,
    diagnose_screener,
    diagnose_setup_a,
    diagnose_setup_b,
)
from engine.setups import detect_setup_a, detect_setup_b
from engine.screener import resolve_candidate_direction


def make_ohlcv(
    n: int = 250,
    *,
    base: float = 100.0,
    daily_return: float = 0.002,
    noise: float = 0.0,
    volume: float | None = None,
    volume_tail: float | None = None,
    tail_bars: int = 5,
) -> pd.DataFrame:
    """Serie OHLCV sintetica per test controllati."""
    rng = np.random.default_rng(42)
    idx = pd.date_range("2020-01-01", periods=n, freq="D", tz="UTC")
    rets = np.full(n, daily_return) + rng.normal(0, noise, n)
    close = base * np.cumprod(1 + rets)
    high = close * 1.005
    low = close * 0.995
    open_ = np.roll(close, 1)
    open_[0] = base
    vol = np.full(n, volume if volume is not None else 1_000_000.0)
    if volume_tail is not None:
        vol[-tail_bars:] = volume_tail
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": vol},
        index=idx,
    )


def _e50_last(df: pd.DataFrame) -> float:
    from engine.indicators import ema

    return float(ema(df["close"], 50).iloc[-1])


def _coherence_setup_a(df: pd.DataFrame, direction: str) -> None:
    diag = diagnose_setup_a(df, direction)
    detect = detect_setup_a(df, direction)
    assert diag["eligible"] == (detect is not None)


def _coherence_setup_b(df: pd.DataFrame, direction: str) -> None:
    diag = diagnose_setup_b(df, direction)
    detect = detect_setup_b(df, direction)
    assert diag["eligible"] == (detect is not None)


# ---------- RS / screener ----------


def test_rs_borderline_long():
    df = make_ohlcv()
    last = float(df["close"].iloc[-1])
    e50 = _e50_last(df)
    last = e50 + 1  # forza sopra EMA50
    df.iloc[-1, df.columns.get_loc("close")] = last
    df.iloc[-1, df.columns.get_loc("high")] = last * 1.01
    df.iloc[-1, df.columns.get_loc("low")] = last * 0.99

    fail = diagnose_screener(df, 0.79, "long", True, False)
    rs_f = next(f for f in fail if f["id"] == "rs_long")
    assert rs_f["status"] == "fail"

    pass_ = diagnose_screener(df, 0.81, "long", True, False)
    rs_p = next(f for f in pass_ if f["id"] == "rs_long")
    assert rs_p["status"] == "pass"


def test_rs_borderline_short():
    df = make_ohlcv(daily_return=-0.002)
    last = _e50_last(df) - 1
    df.iloc[-1, df.columns.get_loc("close")] = last
    df.iloc[-1, df.columns.get_loc("high")] = last * 1.01
    df.iloc[-1, df.columns.get_loc("low")] = last * 0.99

    fail = diagnose_screener(df, 0.21, "short", False, True)
    assert next(f for f in fail if f["id"] == "rs_short")["status"] == "fail"

    pass_ = diagnose_screener(df, 0.19, "short", False, True)
    assert next(f for f in pass_ if f["id"] == "rs_short")["status"] == "pass"


def test_trend_ema50_long_fail():
    df = make_ohlcv()
    e50 = _e50_last(df)
    df.iloc[-1, df.columns.get_loc("close")] = e50 - 5
    f = diagnose_screener(df, 0.9, "long", True, False)
    assert next(x for x in f if x["id"] == "trend_ema50")["status"] == "fail"


def test_resolve_candidate_direction_matches_screener():
    df = make_ohlcv()
    last = float(df["close"].iloc[-1])
    e50 = _e50_last(df)
    assert resolve_candidate_direction(0.85, last, e50, True, True) == "long"
    assert resolve_candidate_direction(0.15, e50 - 1, e50, True, True) == "short"
    assert resolve_candidate_direction(0.5, last, e50, True, True) is None


# ---------- Setup A ----------


def test_setup_a_volume_declining_fail():
    df = make_ohlcv(volume=500_000, volume_tail=2_000_000)
    for direction in ("long", "short"):
        d = diagnose_setup_a(df, direction)
        vol = next(f for f in d["filters"] if f["id"] == "setup_a_volume")
        assert vol["status"] == "fail"


def test_setup_a_coherence_on_fixtures():
    fixtures = [
        make_ohlcv(daily_return=0.003, noise=0.001),
        make_ohlcv(daily_return=-0.003, noise=0.001),
        make_ohlcv(daily_return=0.0, noise=0.02),
        make_ohlcv(daily_return=0.001, volume=1e6, volume_tail=5e5),
        make_ohlcv(n=230),  # too short
        make_ohlcv(daily_return=-0.001, noise=0.015),
    ]
    for df in fixtures:
        for direction in ("long", "short"):
            _coherence_setup_a(df, direction)


# ---------- Setup B ----------


def test_setup_b_coherence_on_fixtures():
    fixtures = [
        make_ohlcv(daily_return=0.002, noise=0.0001),
        make_ohlcv(daily_return=-0.002, noise=0.0001),
        make_ohlcv(daily_return=0.0, noise=0.05),
        make_ohlcv(n=200),
    ]
    for df in fixtures:
        for direction in ("long", "short"):
            _coherence_setup_b(df, direction)


def test_setup_b_squeeze_fail_on_volatile_series():
    df = make_ohlcv(daily_return=0.0, noise=0.08)
    d = diagnose_setup_b(df, "long")
    sq = next(f for f in d["filters"] if f["id"] == "setup_b_squeeze")
    assert sq["status"] == "fail"
    assert "Squeeze assente" in sq["message"]


# ---------- Regime ----------


def test_regime_halt():
    regime = {
        "mode": "halt",
        "long_allowed": False,
        "short_allowed": False,
        "half_size": False,
    }
    for direction in ("long", "short"):
        f = diagnose_regime(regime, direction)
        assert f[0]["status"] == "fail"


def test_regime_crypto_mixed_symbol_warn():
    regime = {
        "mode": "mixed",
        "long_allowed": True,
        "short_allowed": True,
        "half_size": True,
    }
    f = diagnose_regime(regime, "long", market="crypto", symbol="SOLUSDT")
    mixed = next(x for x in f if x["id"] == "crypto_mixed_symbol")
    assert mixed["status"] == "warn"


def test_stock_regime_halt_vix():
    n = 250
    idx = pd.date_range("2020-01-01", periods=n, freq="D", tz="UTC")
    spy = make_ohlcv(n).set_index(idx)
    qqq = make_ohlcv(n).set_index(idx)
    regime = regime_mod.stock_regime(spy, qqq, VIX_HALT + 1)
    assert regime["mode"] == "halt"
    assert not regime["long_allowed"]


# ---------- diagnose_asset / blockers ----------


def test_diagnose_asset_blockers_when_not_eligible():
    regime = {
        "mode": "short",
        "long_allowed": False,
        "short_allowed": True,
        "half_size": False,
    }
    df = make_ohlcv(daily_return=0.005)
    d = diagnose_asset("crypto", "TESTUSDT", df, regime, rs_score=0.9)
    assert not d["watchlist_eligible"]
    assert len(d["blockers"]) >= 1


def test_filter_status_values():
    df = make_ohlcv()
    d = diagnose_setup_a(df, "long")
    for f in d["filters"]:
        assert f["status"] in ("pass", "fail", "skip", "warn")


# ---------- Integration (rete opzionale) ----------


@pytest.mark.integration
def test_real_btc_setup_coherence():
    pytest.importorskip("httpx")
    from data import binance_client

    try:
        df = binance_client.klines("BTCUSDT", "1d", 400).iloc[:-1]
    except Exception as exc:
        pytest.skip(f"Binance non disponibile: {exc}")
    if len(df) < 220:
        pytest.skip("storico BTC insufficiente")
    for direction in ("long", "short"):
        _coherence_setup_a(df, direction)
        _coherence_setup_b(df, direction)


@pytest.mark.integration
def test_real_spy_setup_coherence():
    from data import stocks_client

    try:
        data = stocks_client.daily_history(["SPY"], threads=False, min_bars=250)
    except Exception as exc:
        pytest.skip(f"Yahoo non disponibile: {exc}")
    df = data.get("SPY")
    if df is None or len(df) < 220:
        pytest.skip("storico SPY insufficiente")
    for direction in ("long", "short"):
        _coherence_setup_a(df, direction)
        _coherence_setup_b(df, direction)
