/** Metriche del journal per il protocollo di validazione (§11 della strategia). */
import { listTrades } from "../db/database";
import type { Metrics, Trade } from "../engine/types";

export const VALIDATION_TRADES = 50;
export const MIN_EXPECTANCY = 0.15;
export const MIN_PROFIT_FACTOR = 1.4;

export function computeMetrics(): Metrics {
  const trades = listTrades();
  const closed = trades.filter(
    (t): t is Trade & { r_result: number } =>
      t.status === "closed" && t.r_result != null
  );
  const openTrades = trades.filter((t) => t.status === "open");

  const n = closed.length;
  const base = {
    total_trades: trades.length,
    open_trades: openTrades.length,
    closed_trades: n,
    validation_target: VALIDATION_TRADES,
    validation_progress_pct: Math.round(Math.min(n / VALIDATION_TRADES, 1) * 1000) / 10,
  };

  if (n === 0) {
    return {
      ...base,
      win_rate: null,
      expectancy: null,
      profit_factor: null,
      avg_win_r: null,
      avg_loss_r: null,
      max_drawdown_r: null,
      equity_curve: [],
      validation_passed: false,
      mistakes: 0,
    };
  }

  const rs = [...closed]
    .sort((a, b) => (a.closed_at ?? "").localeCompare(b.closed_at ?? ""))
    .map((t) => t.r_result);

  const wins = rs.filter((r) => r > 0);
  const losses = rs.filter((r) => r <= 0);

  const winRate = wins.length / n;
  const avgWin = wins.length ? wins.reduce((a, b) => a + b, 0) / wins.length : 0;
  const avgLoss = losses.length ? Math.abs(losses.reduce((a, b) => a + b, 0) / losses.length) : 0;
  const expectancy = rs.reduce((a, b) => a + b, 0) / n;
  const grossWin = wins.reduce((a, b) => a + b, 0);
  const grossLoss = Math.abs(losses.reduce((a, b) => a + b, 0));
  const profitFactor = grossLoss > 0 ? grossWin / grossLoss : Infinity;

  const curve: { trade: number; cum_r: number }[] = [];
  let cum = 0;
  let peak = 0;
  let maxDd = 0;
  for (let i = 0; i < rs.length; i++) {
    cum += rs[i];
    peak = Math.max(peak, cum);
    maxDd = Math.max(maxDd, peak - cum);
    curve.push({ trade: i + 1, cum_r: Math.round(cum * 100) / 100 });
  }

  const validationPassed =
    n >= VALIDATION_TRADES &&
    expectancy > MIN_EXPECTANCY &&
    profitFactor > MIN_PROFIT_FACTOR;

  return {
    ...base,
    win_rate: Math.round(winRate * 1000) / 10,
    expectancy: Math.round(expectancy * 1000) / 1000,
    profit_factor:
      profitFactor !== Infinity ? Math.round(profitFactor * 100) / 100 : null,
    avg_win_r: Math.round(avgWin * 100) / 100,
    avg_loss_r: Math.round(avgLoss * 100) / 100,
    max_drawdown_r: Math.round(maxDd * 100) / 100,
    equity_curve: curve,
    validation_passed: validationPassed,
    mistakes: closed.filter((t) => t.mistake).length,
  };
}
