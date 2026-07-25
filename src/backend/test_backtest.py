"""Unit test backtester — meccanica fill/exit e assenza di look-ahead, nessuna rete."""
from __future__ import annotations

import pandas as pd

from engine.backtest import (
    Trade,
    aggregate,
    check_entry,
    check_exit,
    simulate_symbol,
    trade_costs,
    wilson_ci,
)

NO_COSTS = {"taker_fee": 0.0, "funding_daily": 0.0}
WARMUP = 220


def make_df(custom: list[dict]) -> pd.DataFrame:
    """220 barre piatte di warmup a 100, poi le barre custom."""
    rows = [{"open": 100.0, "high": 100.5, "low": 99.5, "close": 100.0, "volume": 1e6}] * WARMUP
    rows = rows + custom
    idx = pd.date_range("2020-01-01", periods=len(rows), freq="D", tz="UTC")
    return pd.DataFrame(rows, index=idx)


def signal_on(df: pd.DataFrame, bar_offset: int, sig: dict):
    """signal_fn che emette il segnale solo per la barra warmup+bar_offset."""
    target_date = df.index[WARMUP + bar_offset]

    def fn(hist: pd.DataFrame, date: pd.Timestamp):
        return dict(sig) if date == target_date else None

    return fn


LONG_SIG = {"setup": "A", "direction": "long", "entry_trigger": 105.0, "stop": 95.0}
SHORT_SIG = {"setup": "B", "direction": "short", "entry_trigger": 95.0, "stop": 105.0}


def run(df: pd.DataFrame, fn, **kw) -> list[Trade]:
    return simulate_symbol(
        df, fn, market="crypto", symbol="TESTUSDT", cost_kwargs=NO_COSTS, **kw
    )


# ---------- Wilson CI ----------


def test_wilson_ci_sane():
    lo, hi = wilson_ci(60, 100)
    assert 0.0 <= lo < 0.6 < hi <= 1.0
    assert abs((lo + hi) / 2 - 0.6) < 0.02  # centro vicino a p
    assert wilson_ci(0, 0) == (0.0, 0.0)
    lo1, hi1 = wilson_ci(6, 10)
    assert hi1 - lo1 > hi - lo  # meno campione → intervallo più largo


# ---------- Entry fill ----------


def test_entry_fill_at_trigger_long():
    bar = pd.Series({"open": 100.0, "high": 106.0, "low": 99.0, "close": 104.0})
    assert check_entry(bar, "long", 105.0) == 105.0


def test_entry_gap_fills_at_open_long():
    bar = pd.Series({"open": 108.0, "high": 110.0, "low": 107.0, "close": 109.0})
    assert check_entry(bar, "long", 105.0) == 108.0  # gap oltre il trigger → open


def test_entry_no_fill_when_trigger_not_reached():
    bar = pd.Series({"open": 100.0, "high": 104.0, "low": 99.0, "close": 103.0})
    assert check_entry(bar, "long", 105.0) is None


def test_entry_fill_short_gap():
    bar = pd.Series({"open": 92.0, "high": 93.0, "low": 90.0, "close": 91.0})
    assert check_entry(bar, "short", 95.0) == 92.0


# ---------- Trade completo: target 2R ----------


def test_full_trade_target_2r_long():
    df = make_df([
        {"open": 100, "high": 106, "low": 99, "close": 104, "volume": 1e6},   # entry 105
        {"open": 110, "high": 126, "low": 108, "close": 124, "volume": 1e6},  # target 125
    ])
    trades = run(df, signal_on(df, 0, LONG_SIG))
    assert len(trades) == 1
    t = trades[0]
    assert t.entry == 105.0
    assert t.exit == 125.0  # 105 + 2*(105-95)
    assert t.exit_reason == "target"
    assert t.r_gross == 2.0
    assert t.r_net == 2.0  # costi azzerati


def test_gap_entry_changes_r_base():
    df = make_df([
        {"open": 108, "high": 110, "low": 107, "close": 109, "volume": 1e6},  # gap: fill 108
        {"open": 130, "high": 140, "low": 129, "close": 138, "volume": 1e6},
    ])
    trades = run(df, signal_on(df, 0, LONG_SIG))
    t = trades[0]
    assert t.entry == 108.0
    # target = 108 + 2*(108-95) = 134; barra 2 apre a 130 < 134 e high 140 ≥ 134
    assert t.exit == 134.0
    assert t.r_gross == 2.0


# ---------- Stop con gap-through ----------


def test_stop_gap_through_fills_at_open():
    df = make_df([
        {"open": 100, "high": 106, "low": 99, "close": 104, "volume": 1e6},  # entry 105
        {"open": 90, "high": 92, "low": 88, "close": 91, "volume": 1e6},     # gap sotto stop 95
    ])
    trades = run(df, signal_on(df, 0, LONG_SIG))
    t = trades[0]
    assert t.exit == 90.0  # open, non lo stop
    assert t.exit_reason == "stop_gap"
    assert t.r_gross == -1.5  # (90-105)/10


def test_stop_normal_fill_at_stop():
    df = make_df([
        {"open": 100, "high": 106, "low": 99, "close": 104, "volume": 1e6},
        {"open": 98, "high": 99, "low": 94, "close": 96, "volume": 1e6},  # low sotto 95
    ])
    trades = run(df, signal_on(df, 0, LONG_SIG))
    t = trades[0]
    assert t.exit == 95.0
    assert t.exit_reason == "stop"
    assert t.r_gross == -1.0


def test_same_bar_stop_out():
    # La barra di entrata rompe il trigger E lo stop: chiusura pessimistica a -1R.
    df = make_df([
        {"open": 100, "high": 106, "low": 94, "close": 96, "volume": 1e6},
    ])
    trades = run(df, signal_on(df, 0, LONG_SIG))
    assert len(trades) == 1
    assert trades[0].exit_reason == "stop_same_bar"
    assert trades[0].r_gross == -1.0


def test_stop_checked_before_target_same_bar():
    # Barra che tocca sia stop sia target dopo l'entrata → esce a stop (pessimistico).
    df = make_df([
        {"open": 100, "high": 106, "low": 99, "close": 104, "volume": 1e6},   # entry 105
        {"open": 100, "high": 130, "low": 90, "close": 120, "volume": 1e6},   # stop e target
    ])
    trades = run(df, signal_on(df, 0, LONG_SIG))
    assert trades[0].exit_reason == "stop"
    assert trades[0].r_gross == -1.0


# ---------- Time stop ----------


def test_time_stop_exit_at_close():
    flat = {"open": 104, "high": 104.5, "low": 103.5, "close": 104, "volume": 1e6}
    df = make_df([
        {"open": 100, "high": 106, "low": 99, "close": 104, "volume": 1e6},  # entry
        dict(flat), dict(flat), dict(flat), dict(flat),
    ])
    trades = run(df, signal_on(df, 0, LONG_SIG), time_stop=3)
    assert len(trades) == 1
    assert trades[0].exit_reason == "time"
    assert trades[0].bars_held == 3
    assert trades[0].exit == 104.0


# ---------- No look-ahead ----------


def test_no_look_ahead_hist_excludes_current_bar():
    seen: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    df = make_df([
        {"open": 100, "high": 106, "low": 99, "close": 104, "volume": 1e6},
        {"open": 110, "high": 126, "low": 108, "close": 124, "volume": 1e6},
    ])

    def spy_fn(hist: pd.DataFrame, date: pd.Timestamp):
        seen.append((hist.index[-1], date))
        return None

    run(df, spy_fn)
    assert len(seen) > 0
    for last_hist_date, current_date in seen:
        assert last_hist_date < current_date  # mai la barra corrente nella history


# ---------- Short ----------


def test_full_trade_short_target():
    df = make_df([
        {"open": 100, "high": 101, "low": 94, "close": 96, "volume": 1e6},   # entry short 95
        {"open": 90, "high": 91, "low": 74, "close": 76, "volume": 1e6},     # target 75
    ])
    trades = run(df, signal_on(df, 0, SHORT_SIG))
    t = trades[0]
    assert t.entry == 95.0
    assert t.exit == 75.0  # 95 - 2*(105-95)
    assert t.r_gross == 2.0


# ---------- Costi ----------


def test_crypto_costs_reduce_net_r():
    df = make_df([
        {"open": 100, "high": 106, "low": 99, "close": 104, "volume": 1e6},
        {"open": 110, "high": 126, "low": 108, "close": 124, "volume": 1e6},
    ])
    trades = simulate_symbol(
        df, signal_on(df, 0, LONG_SIG), market="crypto", symbol="TESTUSDT"
    )
    t = trades[0]
    assert t.r_gross == 2.0
    assert t.cost_r > 0
    assert t.r_net < t.r_gross


def test_stock_costs_min_commission():
    # 10 share → commissione 0.01*10=0.1 < min 1$ → 2 lati * 1$ = 2$
    cost = trade_costs("stocks", 100.0, 110.0, 10.0, 5.0, slippage_pct=0.0)
    assert cost == 2.0


def test_crypto_funding_scales_with_duration():
    c1 = trade_costs("crypto", 100.0, 110.0, 1.0, 1.0, taker_fee=0.0)
    c10 = trade_costs("crypto", 100.0, 110.0, 1.0, 10.0, taker_fee=0.0)
    assert abs(c10 - 10 * c1) < 1e-9


# ---------- Aggregati ----------


def test_aggregate_metrics():
    def mk(r: float) -> Trade:
        d = pd.Timestamp("2024-01-01", tz="UTC")
        return Trade("X", "crypto", "A", "long", d, d, 100, 100, "target", 1, r, 0.0, r)

    trades = [mk(2.0), mk(-1.0), mk(2.0), mk(-1.0), mk(-1.0)]
    agg = aggregate(trades)
    assert agg["n_trades"] == 5
    assert agg["wins"] == 2
    assert agg["win_rate"] == 0.4
    assert agg["expectancy_r"] == 0.2
    assert agg["profit_factor"] == round(4 / 3, 3)
    # equity: 2,1,3,2,1 → picco 3, minimo dopo il picco 1 → DD 2
    assert agg["max_drawdown_r"] == 2.0
    lo, hi = agg["win_rate_ci95"]
    assert lo < 0.4 < hi
