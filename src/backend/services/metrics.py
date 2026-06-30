"""Metriche del journal per il protocollo di validazione (§11 della strategia)."""
import database

VALIDATION_TRADES = 50
MIN_EXPECTANCY = 0.15
MIN_PROFIT_FACTOR = 1.4


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
    }
    if n == 0:
        return {**base, "win_rate": None, "expectancy": None, "profit_factor": None,
                "avg_win_r": None, "avg_loss_r": None, "max_drawdown_r": None,
                "equity_curve": [], "validation_passed": False, "mistakes": 0}

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

    # Curva di equity in R e max drawdown
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
    return {
        **base,
        "win_rate": round(win_rate * 100, 1),
        "expectancy": round(expectancy, 3),
        "profit_factor": round(profit_factor, 2) if profit_factor != float("inf") else None,
        "avg_win_r": round(avg_win, 2),
        "avg_loss_r": round(avg_loss, 2),
        "max_drawdown_r": round(max_dd, 2),
        "equity_curve": curve,
        "validation_passed": validation_passed,
        "mistakes": sum(1 for t in closed if t["mistake"]),
    }
