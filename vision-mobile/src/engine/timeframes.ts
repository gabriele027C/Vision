/**
 * Detection multi-timeframe gerarchica (FASE 3) — speculare a engine/timeframes.py.
 *
 * D/4H = ingresso watchlist; 1H/15m = timing solo su asset già in watchlist.
 * Invalidation ATR multipliers: ipotesi descrittive, non stop validati.
 */
import { TF_PARAMS, TIMING_ALERT_COOLDOWN_S, TIMING_TFS, type TfParams } from "../config";
import { atr, bollingerWidth, ema, rvol } from "./indicators";
import type { OHLCVBar } from "./types";

function roundPx(x: number): number {
  return Number(Number(x).toPrecision(6));
}

export function tfParams(timeframe: keyof typeof TF_PARAMS): TfParams {
  return TF_PARAMS[timeframe];
}

export function closedKlines(bars: OHLCVBar[]): OHLCVBar[] {
  if (!bars.length) return [];
  return bars.length > 1 ? bars.slice(0, -1) : [];
}

export interface CompressionMetrics {
  timeframe: string;
  squeeze: boolean;
  context_ok: boolean;
  atr: number;
  trigger: number;
  stop: number;
  stop_dist: number;
  invalidation_atr_mult: number;
  rvol: number;
  last: number;
  rng_high: number;
  rng_low: number;
  bbw_last: number;
  bbw_thresh: number;
}

/** Quantile lineare (pandas Series.quantile default) — riferimento Python. */
function quantileLinear(sortedAsc: number[], q: number): number {
  if (!sortedAsc.length) return NaN;
  if (sortedAsc.length === 1) return sortedAsc[0];
  const pos = q * (sortedAsc.length - 1);
  const lo = Math.floor(pos);
  const hi = Math.ceil(pos);
  if (lo === hi) return sortedAsc[lo];
  const w = pos - lo;
  return sortedAsc[lo] * (1 - w) + sortedAsc[hi] * w;
}

export function compressionMetrics(
  bars: OHLCVBar[],
  direction: "long" | "short" = "long",
  timeframe: keyof typeof TF_PARAMS = "D"
): CompressionMetrics | null {
  const p = tfParams(timeframe);
  if (bars.length < p.MIN_BARS) return null;

  const close = bars.map((b) => b.close);
  const high = bars.map((b) => b.high);
  const low = bars.map((b) => b.low);
  const volume = bars.map((b) => b.volume);
  const last = close[close.length - 1];
  const emaLen = Math.min(200, close.length - 1);
  const e200 = ema(close, emaLen)[close.length - 1];
  const aArr = atr(high, low, close);
  const a = aArr[aArr.length - 1];
  if (!(a > 0)) return null;

  const bbw = bollingerWidth(close);
  const bbwLast = bbw[bbw.length - 1];
  const look = p.SQUEEZE_LOOKBACK;
  const slice = bbw.slice(bbw.length - look - 1, bbw.length - 1).filter((x) => Number.isFinite(x));
  const sorted = [...slice].sort((x, y) => x - y);
  const bbwThresh = quantileLinear(sorted, 0.1);
  const squeeze = bbwLast <= bbwThresh;

  const rb = p.RANGE_BARS;
  const rngHigh = Math.max(...high.slice(high.length - rb - 1, high.length - 1));
  const rngLow = Math.min(...low.slice(low.length - rb - 1, low.length - 1));
  const inv = p.INVALIDATION_ATR;

  let trigger: number;
  let stop: number;
  let contextOk: boolean;
  if (direction === "long") {
    contextOk = last >= e200;
    trigger = rngHigh;
    stop = trigger - inv * a;
  } else {
    contextOk = last <= e200;
    trigger = rngLow;
    stop = trigger + inv * a;
  }

  const rvSeries = rvol(volume);
  const rvRaw = rvSeries[rvSeries.length - 1];
  const rv = Number.isFinite(rvRaw) ? rvRaw : 0;

  return {
    timeframe,
    squeeze,
    context_ok: contextOk,
    atr: a,
    trigger,
    stop,
    stop_dist: Math.abs(trigger - stop),
    invalidation_atr_mult: inv,
    rvol: rv,
    last,
    rng_high: rngHigh,
    rng_low: rngLow,
    bbw_last: bbwLast,
    bbw_thresh: bbwThresh,
  };
}

export function detectCompression(
  bars: OHLCVBar[],
  direction: "long" | "short" = "long",
  timeframe: keyof typeof TF_PARAMS = "D"
) {
  const m = compressionMetrics(bars, direction, timeframe);
  if (!m || !m.squeeze || !m.context_ok) return null;
  return {
    setup: "B" as const,
    timeframe,
    direction,
    entry_trigger: roundPx(m.trigger),
    stop: roundPx(m.stop),
    atr: roundPx(m.atr),
    invalidation_atr_mult: m.invalidation_atr_mult,
    rvol: Math.round(m.rvol * 100) / 100,
    note:
      `Compressione ${timeframe}: livello di rottura ${roundPx(m.trigger)}, ` +
      `invalidazione ${roundPx(m.stop)} (${m.invalidation_atr_mult}×ATR ${timeframe})`,
  };
}

export class TimingAlertGate {
  private last = new Map<string, number>();
  constructor(private cooldownS = TIMING_ALERT_COOLDOWN_S) {}
  allow(symbol: string, now = Date.now() / 1000): boolean {
    const prev = this.last.get(symbol);
    if (prev != null && now - prev < this.cooldownS) return false;
    this.last.set(symbol, now);
    return true;
  }
}

export function attachTimingToRow(
  row: { entry_trigger?: number },
  lowerTfs: Partial<Record<(typeof TIMING_TFS)[number], OHLCVBar[]>>,
  direction: "long" | "short" = "long"
) {
  const found: Array<ReturnType<typeof detectCompression> & { aligned_with_daily?: boolean }> = [];
  for (const tf of TIMING_TFS) {
    const bars = lowerTfs[tf];
    if (!bars?.length) continue;
    const hist = closedKlines(bars);
    const det = detectCompression(hist, direction, tf);
    if (!det) continue;
    const dailyLevel = row.entry_trigger;
    if (dailyLevel != null && direction === "long" && hist.length) {
      const last = hist[hist.length - 1].close;
      if (last < dailyLevel) {
        found.push({
          ...det,
          note: det.note + " — sotto il livello daily (non timing long)",
          aligned_with_daily: false,
        });
      } else {
        found.push({ ...det, aligned_with_daily: true });
      }
    } else {
      found.push(det);
    }
  }
  return found;
}
