/**
 * Runner Node/TS: stesse fixture → output JSON normalizzato (speculare a run_python.py).
 * Uso: npx tsx parity/run_ts.ts
 */
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { confluenceScore } from "../vision-mobile/src/engine/confluence.ts";
import {
  buildFlowSnapshot,
  classifyCvd,
  classifyOi,
  cvdSlopeNormalized,
  oiDeltasFromHist,
} from "../vision-mobile/src/engine/flow.ts";
import { scenarioIdsForRow } from "../vision-mobile/src/engine/playbook.ts";
import { positionSize } from "../vision-mobile/src/engine/sizing.ts";
import { detectSetupA, detectSetupB } from "../vision-mobile/src/engine/setups.ts";
import { compressionMetrics, detectCompression } from "../vision-mobile/src/engine/timeframes.ts";
import type { OHLCVBar, WatchRow } from "../vision-mobile/src/engine/types.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));
const FIXTURES = join(__dirname, "fixtures", "synthetic.json");

type SizingRaw = Record<string, unknown>;

function normSizing(raw: SizingRaw) {
  if (raw.error != null) {
    return {
      error_present: true,
      liq_safe: raw.liq_safe ?? false,
      liq_price: raw.liq_price ?? null,
      leverage: raw.leverage ?? null,
    };
  }
  const { error: _e, ...rest } = raw;
  return { ...rest, error_present: false };
}

function normMetrics(m: ReturnType<typeof compressionMetrics>) {
  if (!m) return null;
  return {
    timeframe: m.timeframe,
    squeeze: m.squeeze,
    context_ok: m.context_ok,
    atr: m.atr,
    trigger: m.trigger,
    stop: m.stop,
    stop_dist: m.stop_dist,
    invalidation_atr_mult: m.invalidation_atr_mult,
    rvol: m.rvol,
    last: m.last,
    rng_high: m.rng_high,
    rng_low: m.rng_low,
  };
}

function normDetect(d: ReturnType<typeof detectCompression>) {
  if (!d) return null;
  return {
    setup: d.setup,
    timeframe: d.timeframe,
    direction: d.direction,
    entry_trigger: d.entry_trigger,
    stop: d.stop,
    atr: d.atr,
    invalidation_atr_mult: d.invalidation_atr_mult,
    rvol: d.rvol,
  };
}

function normSetup(d: ReturnType<typeof detectSetupA>) {
  if (!d) return null;
  return {
    setup: d.setup,
    direction: d.direction,
    entry_trigger: d.entry_trigger,
    stop: d.stop,
    atr: d.atr,
  };
}

export function run(fixtures?: Record<string, unknown>) {
  const data = (fixtures ??
    JSON.parse(readFileSync(FIXTURES, "utf8"))) as {
    oi_delta_cases: Array<{ delta_24h: number | null }>;
    cvd_slope_cases: Array<{ slope: number | null }>;
    oi_hist: number[];
    oi_bars_per_day: number;
    taker: { volume: number[]; taker_buy_up: number[]; taker_buy_down: number[] };
    ohlcv: Record<string, OHLCVBar[]>;
    compression_tfs: Array<"D" | "4H" | "1H" | "15m">;
    compression_directions: Array<"long" | "short">;
    sizing_cases: Array<{
      id: string;
      capital: number;
      risk_pct: number;
      entry: number;
      stop: number;
      half_size: boolean;
      direction: "long" | "short";
      max_leverage: number | null;
      taker_fee: number;
      market: "crypto" | "stocks";
      funding_est: number | null;
      days_held_est: number;
    }>;
    confluence_rows: Array<Record<string, unknown>>;
    playbook_rows: Array<Record<string, unknown>>;
  };

  const oi_flags = data.oi_delta_cases.map((c) => ({
    delta_24h: c.delta_24h,
    state: classifyOi(c.delta_24h),
  }));
  const cvd_flags = data.cvd_slope_cases.map((c) => ({
    slope: c.slope,
    state: classifyCvd(c.slope),
  }));

  const deltas = oiDeltasFromHist(data.oi_hist, data.oi_bars_per_day);
  const slope_up = cvdSlopeNormalized(data.taker.volume, data.taker.taker_buy_up);
  const slope_down = cvdSlopeNormalized(data.taker.volume, data.taker.taker_buy_down);
  const snap = buildFlowSnapshot({
    oi_value: deltas.oi_value,
    oi_delta_24h: deltas.oi_delta_24h,
    oi_delta_3d: deltas.oi_delta_3d,
    cvd_slope: slope_up,
    price_delta: 0.02,
  });

  const flow = {
    oi_flags,
    cvd_flags,
    oi_deltas: {
      oi_value: deltas.oi_value,
      oi_delta_24h: deltas.oi_delta_24h,
      oi_delta_3d: deltas.oi_delta_3d,
      oi_state: classifyOi(deltas.oi_delta_24h),
    },
    cvd_slopes: {
      up: slope_up,
      up_state: classifyCvd(slope_up),
      down: slope_down,
      down_state: classifyCvd(slope_down),
    },
    snap: {
      oi_state: snap.oi_state,
      cvd_state: snap.cvd_state,
      price_state: snap.price_state,
      combo_key: snap.combo_key,
    },
  };

  const compression: Record<string, unknown> = {};
  for (const tf of data.compression_tfs) {
    const bars = data.ohlcv[tf];
    compression[tf] = {} as Record<string, unknown>;
    for (const direction of data.compression_directions) {
      (compression[tf] as Record<string, unknown>)[direction] = {
        metrics: normMetrics(compressionMetrics(bars, direction, tf)),
        detect: normDetect(detectCompression(bars, direction, tf)),
      };
    }
  }

  const barsD = data.ohlcv.D;
  const levels = {
    setup_a_long: normSetup(detectSetupA(barsD, "long", "crypto")),
    setup_a_short: normSetup(detectSetupA(barsD, "short", "crypto")),
    setup_b_long: normSetup(detectSetupB(barsD, "long", "crypto")),
    setup_b_short: normSetup(detectSetupB(barsD, "short", "crypto")),
  };

  const sizing: Record<string, unknown> = {};
  for (const c of data.sizing_cases) {
    const raw = positionSize(
      c.capital,
      c.risk_pct,
      c.entry,
      c.stop,
      c.half_size,
      c.direction,
      c.max_leverage,
      c.taker_fee,
      c.market,
      c.funding_est,
      c.days_held_est
    ) as SizingRaw;
    sizing[c.id] = normSizing(raw);
  }

  const confluence: Record<string, unknown> = {};
  for (const row of data.confluence_rows) {
    const { id, ...payload } = row;
    confluence[id as string] = confluenceScore(payload as unknown as WatchRow);
  }

  const playbook: Record<string, unknown> = {};
  for (const row of data.playbook_rows) {
    const { id, ...payload } = row;
    playbook[id as string] = {
      scenario_ids: scenarioIdsForRow(payload as unknown as WatchRow),
    };
  }

  return {
    engine: "typescript",
    flow,
    compression,
    levels,
    sizing,
    confluence,
    playbook,
  };
}

// CLI: sempre stampa JSON su stdout quando eseguito con tsx/node.
console.log(JSON.stringify(run(), null, 2));
