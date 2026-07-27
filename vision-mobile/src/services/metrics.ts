/** Metriche del journal — allineate a services/metrics.py (FASE 0). */
import { listTrades } from "../db/database";
import type { Metrics, MetricsBucket, Trade } from "../engine/types";

export const VALIDATION_TRADES = 50;
export const MIN_EXPECTANCY = 0.15;
export const MIN_PROFIT_FACTOR = 1.4;
export const RANDOM_BENCHMARK_WR = 1 / 3;

function groupExpectancy(closed: Trade[], key: keyof Trade): MetricsBucket[] {
  const buckets = new Map<string, number[]>();
  for (const t of closed) {
    const val = t[key];
    if (val == null || val === "") continue;
    const name = String(val);
    const arr = buckets.get(name) ?? [];
    arr.push(t.r_result as number);
    buckets.set(name, arr);
  }
  return [...buckets.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([name, rs]) => {
      const n = rs.length;
      const wins = rs.filter((r) => r > 0).length;
      return {
        key: name,
        n,
        win_rate: n ? Math.round((wins / n) * 1000) / 10 : null,
        expectancy: n ? Math.round((rs.reduce((a, b) => a + b, 0) / n) * 1000) / 1000 : null,
      };
    });
}

function contextBuckets(closed: Trade[]): Metrics["by_context"] {
  function collect(field: keyof Trade, labeler: (v: number) => string): MetricsBucket[] {
    const groups = new Map<string, number[]>();
    for (const t of closed) {
      const raw = t[field];
      if (raw == null) continue;
      const v = Number(raw);
      if (Number.isNaN(v)) continue;
      const label = labeler(v);
      const arr = groups.get(label) ?? [];
      arr.push(t.r_result as number);
      groups.set(label, arr);
    }
    return [...groups.entries()]
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([name, rs]) => {
        const n = rs.length;
        const wins = rs.filter((r) => r > 0).length;
        return {
          key: name,
          n,
          win_rate: Math.round((wins / n) * 1000) / 10,
          expectancy: Math.round((rs.reduce((a, b) => a + b, 0) / n) * 1000) / 1000,
        };
      });
  }

  return {
    rvol: collect("rvol_at_entry", (v) => {
      if (v < 1) return "<1.0";
      if (v < 1.5) return "1.0-1.5";
      if (v < 2) return "1.5-2.0";
      return ">=2.0";
    }),
    funding: collect("funding_at_entry", (v) => {
      if (v >= 0.0005) return "extreme_long_pay";
      if (v <= -0.0005) return "extreme_short_pay";
      if (v > 0) return "positive";
      if (v < 0) return "negative";
      return "flat";
    }),
    oi: collect("oi_at_entry", (v) => {
      // |v|<=1 → Δ frazione; altrimenti livello assoluto (non bucketabile qui)
      if (Math.abs(v) > 1) return "level";
      if (v <= -0.2) return "collapse";
      if (v < -0.05) return "down";
      if (v > 0.05) return "up";
      return "flat";
    }),
  };
}

function scenarioExpectancy(closed: Trade[]): NonNullable<Metrics["by_scenario"]> {
  const groups = new Map<string, number[]>();
  for (const t of closed) {
    for (const sid of t.scenario_ids ?? []) {
      const arr = groups.get(String(sid)) ?? [];
      arr.push(t.r_result as number);
      groups.set(String(sid), arr);
    }
  }
  const out: NonNullable<Metrics["by_scenario"]> = [];
  for (const [sid, rs] of [...groups.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    const n = rs.length;
    if (n < 10) continue;
    const wins = rs.filter((r) => r > 0).length;
    out.push({
      scenario_id: sid,
      n,
      win_rate: Math.round((wins / n) * 1000) / 10,
      expectancy: Math.round((rs.reduce((a, b) => a + b, 0) / n) * 1000) / 1000,
      note: n < 30 ? "statistiche indicative sotto n=30" : null,
    });
  }
  return out;
}

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
    reliable_stats_from_n: 100,
    stats_reliable: n >= 100,
  };

  const emptyExtra = {
    by_timeframe: [] as MetricsBucket[],
    by_pattern: [] as MetricsBucket[],
    by_context: { rvol: [], funding: [], oi: [] } as NonNullable<Metrics["by_context"]>,
    by_scenario: [] as NonNullable<Metrics["by_scenario"]>,
    random_benchmark: {
      expected_wr_pct: Math.round(RANDOM_BENCHMARK_WR * 1000) / 10,
      note: "WR geometrico atteso ~33% con R:R 2:1 (entry casuale). Confronto descrittivo.",
      user_wr_pct: null as number | null,
      delta_wr_pp: null as number | null,
    },
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
      ...emptyExtra,
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

  const userWrPct = Math.round(winRate * 1000) / 10;
  const benchPct = Math.round(RANDOM_BENCHMARK_WR * 1000) / 10;

  return {
    ...base,
    win_rate: userWrPct,
    expectancy: Math.round(expectancy * 1000) / 1000,
    profit_factor:
      profitFactor !== Infinity ? Math.round(profitFactor * 100) / 100 : null,
    avg_win_r: Math.round(avgWin * 100) / 100,
    avg_loss_r: Math.round(avgLoss * 100) / 100,
    max_drawdown_r: Math.round(maxDd * 100) / 100,
    equity_curve: curve,
    validation_passed: validationPassed,
    mistakes: closed.filter((t) => t.mistake).length,
    by_timeframe: groupExpectancy(closed, "timeframe"),
    by_pattern: groupExpectancy(closed, "pattern"),
    by_context: contextBuckets(closed),
    by_scenario: scenarioExpectancy(closed),
    random_benchmark: {
      expected_wr_pct: benchPct,
      note:
        "WR geometrico atteso ~33% con R:R 2:1 (entry casuale). " +
        "Se il tuo WR supera questo livello con n adeguato, la lettura " +
        "discrezionale batte il caso — non è un edge del software.",
      user_wr_pct: userWrPct,
      delta_wr_pp: Math.round((userWrPct - benchPct) * 10) / 10,
    },
  };
}
