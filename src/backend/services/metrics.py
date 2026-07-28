"""Metriche del journal — screening / risk / journaling (nessun claim predittivo).

Il report confronta la lettura discrezionale dell'utente col benchmark geometrico
casuale a R:R 2:1 (WR atteso ≈ 33%). Non è un target di performance del sistema.
"""
from __future__ import annotations

import database
from config import FUNDING_EXTREME, PLAYBOOK_THRESHOLDS, RVOL_BREAKOUT

VALIDATION_TRADES = 50
MIN_EXPECTANCY = 0.15
MIN_PROFIT_FACTOR = 1.4

# Benchmark geometrico: con target 2R e stop 1R, un entry casuale ha WR ≈ 1/3.
RANDOM_BENCHMARK_WR = 1.0 / 3.0


def _group_expectancy(closed: list[dict], key: str) -> list[dict]:
    """Expectancy / WR per valore di `key`, solo trade con campo valorizzato."""
    buckets: dict[str, list[float]] = {}
    for t in closed:
        val = t.get(key)
        if val is None or val == "":
            continue
        buckets.setdefault(str(val), []).append(float(t["r_result"]))
    out = []
    for name, rs in sorted(buckets.items()):
        n = len(rs)
        wins = sum(1 for r in rs if r > 0)
        out.append({
            "key": name,
            "n": n,
            "win_rate": round(wins / n * 100, 1) if n else None,
            "expectancy": round(sum(rs) / n, 3) if n else None,
        })
    return out


def _context_buckets(closed: list[dict]) -> dict[str, list[dict]]:
    """Bucket di contesto (RVOL / funding / OI) — soglie da config, zero hardcode."""
    rvol_thr = PLAYBOOK_THRESHOLDS.get("rvol", {})
    rvol_high = float(rvol_thr.get("high", 1.5))
    rvol_low = float(rvol_thr.get("low", 1.0))
    oi_thr = PLAYBOOK_THRESHOLDS["oi"]
    oi_up = float(oi_thr["up_pct_24h"])
    oi_down = float(oi_thr["down_pct_24h"])
    oi_collapse = float(oi_thr["collapse_pct_24h"])

    def bucket_rvol(v: float) -> str:
        if v < rvol_low:
            return f"<{rvol_low}"
        if v < rvol_high:
            return f"{rvol_low}-{rvol_high}"
        if v < RVOL_BREAKOUT:
            return f"{rvol_high}-{RVOL_BREAKOUT}"
        return f">={RVOL_BREAKOUT}"

    def bucket_funding(v: float) -> str:
        if v >= FUNDING_EXTREME:
            return "extreme_long_pay"
        if v <= -FUNDING_EXTREME:
            return "extreme_short_pay"
        if v > 0:
            return "positive"
        if v < 0:
            return "negative"
        return "flat"

    def bucket_oi(v: float) -> str:
        # |v|<=1 → Δ frazione (FASE 4 può salvare delta); altrimenti livello assoluto.
        if abs(v) > 1.0:
            return "level"
        if v <= oi_collapse:
            return "collapse"
        if v <= oi_down:
            return "down"
        if v >= oi_up:
            return "up"
        return "flat"

    def collect(field: str, labeler) -> list[dict]:
        groups: dict[str, list[float]] = {}
        for t in closed:
            raw = t.get(field)
            if raw is None:
                continue
            try:
                label = labeler(float(raw))
            except (TypeError, ValueError):
                continue
            groups.setdefault(label, []).append(float(t["r_result"]))
        rows = []
        for name, rs in sorted(groups.items()):
            n = len(rs)
            wins = sum(1 for r in rs if r > 0)
            rows.append({
                "key": name,
                "n": n,
                "win_rate": round(wins / n * 100, 1),
                "expectancy": round(sum(rs) / n, 3),
            })
        return rows

    return {
        "rvol": collect("rvol_at_entry", bucket_rvol),
        "funding": collect("funding_at_entry", bucket_funding),
        "oi": collect("oi_at_entry", bucket_oi),
    }

def _scenario_expectancy(closed: list[dict]) -> list[dict]:
    """Expectancy per scenario_id (playbook). Nota: sotto n=30 indicative."""
    groups: dict[str, list[float]] = {}
    for t in closed:
        ids = t.get("scenario_ids") or []
        if isinstance(ids, str):
            continue
        for sid in ids:
            groups.setdefault(str(sid), []).append(float(t["r_result"]))
    out = []
    for sid, rs in sorted(groups.items()):
        n = len(rs)
        if n < 10:
            continue
        wins = sum(1 for r in rs if r > 0)
        out.append({
            "scenario_id": sid,
            "n": n,
            "win_rate": round(wins / n * 100, 1),
            "expectancy": round(sum(rs) / n, 3),
            "note": "statistiche indicative sotto n=30" if n < 30 else None,
        })
    return out


def compute_metrics() -> dict:
    trades = database.list_trades()
    closed = [t for t in trades if t["status"] == "closed" and t["r_result"] is not None]
    open_trades = [t for t in trades if t["status"] == "open"]

    n = len(closed)
    base = {
        "total_trades": len(trades),
        "open_trades": len(open_trades),
        "closed_trades": n,
        "validation_target": VALIDATION_TRADES,
        "validation_progress_pct": round(min(n / VALIDATION_TRADES, 1.0) * 100, 1),
        "reliable_stats_from_n": 100,
        "stats_reliable": n >= 100,
    }
    empty_extra = {
        "by_timeframe": [],
        "by_pattern": [],
        "by_context": {"rvol": [], "funding": [], "oi": []},
        "by_scenario": [],
        "random_benchmark": {
            "expected_wr_pct": round(RANDOM_BENCHMARK_WR * 100, 1),
            "note": "WR geometrico atteso ~33% con R:R 2:1 (entry casuale). Confronto descrittivo.",
            "user_wr_pct": None,
            "delta_wr_pp": None,
        },
    }
    if n == 0:
        return {
            **base,
            "win_rate": None, "expectancy": None, "profit_factor": None,
            "avg_win_r": None, "avg_loss_r": None, "max_drawdown_r": None,
            "equity_curve": [], "validation_passed": False, "mistakes": 0,
            **empty_extra,
        }

    rs = [t["r_result"] for t in sorted(closed, key=lambda t: t["closed_at"] or "")]
    wins = [r for r in rs if r > 0]
    losses = [r for r in rs if r <= 0]

    win_rate = len(wins) / n
    avg_win = sum(wins) / len(wins) if wins else 0.0
    avg_loss = abs(sum(losses) / len(losses)) if losses else 0.0
    expectancy = sum(rs) / n
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = (gross_win / gross_loss) if gross_loss > 0 else float("inf")

    curve, cum, peak, max_dd = [], 0.0, 0.0, 0.0
    for i, r in enumerate(rs):
        cum += r
        peak = max(peak, cum)
        max_dd = max(max_dd, peak - cum)
        curve.append({"trade": i + 1, "cum_r": round(cum, 2)})

    validation_passed = (
        n >= VALIDATION_TRADES
        and expectancy > MIN_EXPECTANCY
        and profit_factor > MIN_PROFIT_FACTOR
    )

    user_wr_pct = round(win_rate * 100, 1)
    bench_pct = round(RANDOM_BENCHMARK_WR * 100, 1)

    return {
        **base,
        "win_rate": user_wr_pct,
        "expectancy": round(expectancy, 3),
        "profit_factor": round(profit_factor, 2) if profit_factor != float("inf") else None,
        "avg_win_r": round(avg_win, 2),
        "avg_loss_r": round(avg_loss, 2),
        "max_drawdown_r": round(max_dd, 2),
        "equity_curve": curve,
        "validation_passed": validation_passed,
        "mistakes": sum(1 for t in closed if t["mistake"]),
        "by_timeframe": _group_expectancy(closed, "timeframe"),
        "by_pattern": _group_expectancy(closed, "pattern"),
        "by_context": _context_buckets(closed),
        "by_scenario": _scenario_expectancy(closed),
        "random_benchmark": {
            "expected_wr_pct": bench_pct,
            "note": (
                "WR geometrico atteso ~33% con R:R 2:1 (entry casuale). "
                "Se il tuo WR supera questo livello con n adeguato, la lettura "
                "discrezionale batte il caso — non è un edge del software."
            ),
            "user_wr_pct": user_wr_pct,
            "delta_wr_pp": round(user_wr_pct - bench_pct, 1),
        },
    }
