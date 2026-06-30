/** Selezione asset (§3): forza relativa vs benchmark + RVOL + filtro trend. */
import { RS_BOTTOM_PERCENTILE, RS_TOP_PERCENTILE } from "../config";
import { ema, pctReturn, rvol } from "./indicators";
import type { OHLCVBar } from "./types";

export interface ScreenerCandidate {
  symbol: string;
  direction: "long" | "short";
  rs_score: number;
  rvol: number;
  last_price: number;
}

function rankPct(raw: Record<string, number>): Record<string, number> {
  const syms = Object.keys(raw);
  const n = syms.length;
  if (n === 0) return {};
  const out: Record<string, number> = {};
  for (const sym of syms) {
    const v = raw[sym];
    let less = 0;
    let equal = 0;
    for (const other of syms) {
      const ov = raw[other];
      if (ov < v) less++;
      else if (ov === v) equal++;
    }
    out[sym] = (less + equal * 0.5) / n;
  }
  return out;
}

export function rsScores(
  data: Record<string, OHLCVBar[]>,
  bench: OHLCVBar[]
): Record<string, number> {
  const benchClose = bench.map((b) => b.close);
  const b20 = pctReturn(benchClose, 20);
  const b60 = pctReturn(benchClose, 60);
  const raw: Record<string, number> = {};
  for (const [sym, bars] of Object.entries(data)) {
    const close = bars.map((b) => b.close);
    const r20 = pctReturn(close, 20) - b20;
    const r60 = pctReturn(close, 60) - b60;
    raw[sym] = 0.5 * r20 + 0.5 * r60;
  }
  if (Object.keys(raw).length === 0) return {};
  return rankPct(raw);
}

export function resolveCandidateDirection(
  score: number,
  last: number,
  e50: number,
  longAllowed: boolean,
  shortAllowed: boolean
): "long" | "short" | null {
  if (longAllowed && score >= RS_TOP_PERCENTILE && last > e50) return "long";
  if (shortAllowed && score <= RS_BOTTOM_PERCENTILE && last < e50) return "short";
  return null;
}

export function naturalDirection(
  score: number,
  last: number,
  e50: number
): "long" | "short" | null {
  if (score >= RS_TOP_PERCENTILE && last > e50) return "long";
  if (score <= RS_BOTTOM_PERCENTILE && last < e50) return "short";
  return null;
}

export function classifyCandidates(
  data: Record<string, OHLCVBar[]>,
  scores: Record<string, number>,
  longAllowed: boolean,
  shortAllowed: boolean
): ScreenerCandidate[] {
  const out: ScreenerCandidate[] = [];
  for (const [sym, bars] of Object.entries(data)) {
    const score = scores[sym];
    if (score == null || bars.length < 220) continue;

    const close = bars.map((b) => b.close);
    const last = close[close.length - 1];
    const e50Series = ema(close, 50);
    const e50 = e50Series[e50Series.length - 1];
    const rvSeries = rvol(bars.map((b) => b.volume));
    const rvVal = rvSeries[rvSeries.length - 1];
    const rv = rvVal != null && !Number.isNaN(rvVal) ? rvVal : 0;

    const direction = resolveCandidateDirection(score, last, e50, longAllowed, shortAllowed);
    if (direction == null) continue;

    out.push({
      symbol: sym,
      direction,
      rs_score: Math.round(score * 1000) / 1000,
      rvol: Math.round(rv * 100) / 100,
      last_price: last,
    });
  }
  out.sort((a, b) =>
    a.direction === "short" ? a.rs_score - b.rs_score : b.rs_score - a.rs_score
  );
  return out;
}
