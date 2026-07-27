/** Selezione asset: forza relativa vs benchmark + RVOL + trend EMA50.
 * FASE 2: RS percentile non esclude — solo ordina. Regime non filtra.
 */
import { RVOL_HARD_FILTER, RVOL_INTEREST } from "../config";
import { ema, pctReturn, rvol } from "./indicators";
import type { OHLCVBar } from "./types";

export interface ScreenerCandidate {
  symbol: string;
  direction: "long" | "short";
  rs_score: number;
  rvol: number;
  last_price: number;
  rank_score: number;
}

/** Punteggio combinato 0.7*RS + 0.3*RVOL cappato — speculare a rank_score in screener.py. */
export function rankScore(rs: number, rv: number, direction: "long" | "short"): number {
  const strength = direction === "long" ? rs : 1 - rs;
  const volComponent = Math.min(rv / RVOL_INTEREST, 2) / 2;
  return 0.7 * strength + 0.3 * volComponent;
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

/** Direzione da trend EMA50 (RS/regime non escludono). */
export function resolveCandidateDirection(
  _score: number,
  last: number,
  e50: number,
  _longAllowed = true,
  _shortAllowed = true
): "long" | "short" | null {
  if (last > e50) return "long";
  if (last < e50) return "short";
  return null;
}

export function naturalDirection(
  _score: number,
  last: number,
  e50: number
): "long" | "short" | null {
  if (last > e50) return "long";
  if (last < e50) return "short";
  return null;
}

export function classifyCandidates(
  data: Record<string, OHLCVBar[]>,
  scores: Record<string, number>,
  _longAllowed = true,
  _shortAllowed = true,
  rvolHardFilter: boolean | null = null
): ScreenerCandidate[] {
  const hardFilter = rvolHardFilter ?? RVOL_HARD_FILTER;
  const out: ScreenerCandidate[] = [];
  for (const [sym, bars] of Object.entries(data)) {
    const score = scores[sym];
    if (score == null || bars.length < 220) continue;

    const close = bars.map((b) => b.close);
    const last = close[close.length - 1];
    const e50 = ema(close, 50)[close.length - 1];
    const rvSeries = rvol(bars.map((b) => b.volume));
    const rvRaw = rvSeries[rvSeries.length - 1];
    const rv = Number.isFinite(rvRaw) ? rvRaw : 0;

    const direction = resolveCandidateDirection(score, last, e50);
    if (!direction) continue;
    if (hardFilter && rv < RVOL_INTEREST) continue;

    out.push({
      symbol: sym,
      direction,
      rs_score: Math.round(score * 1000) / 1000,
      rvol: Math.round(rv * 100) / 100,
      last_price: last,
      rank_score: Math.round(rankScore(score, rv, direction) * 10000) / 10000,
    });
  }
  out.sort((a, b) => b.rank_score - a.rank_score);
  return out;
}
