/**
 * Confluence score 0–100: SOLO ordinamento (FASE 5).
 * Speculare a engine/confluence.py — stessi pesi, stessa rinorm su n/d.
 */
import {
  CONFLUENCE_WEIGHTS,
  FUNDING_EXTREME,
  PLAYBOOK_THRESHOLDS,
  RVOL_INTEREST,
} from "../config";
import type { WatchRow } from "./types";

type Breakdown = {
  weight: number;
  raw: number | null;
  contrib: number | null;
  status: "ok" | "n/d";
  weight_norm?: number;
};

function scoreTech(row: WatchRow): number | null {
  if (!row.setup) return null;
  return (row.entry_tf ?? "D") === "D" ? 1.0 : 0.85;
}

function scoreRs(row: WatchRow): number | null {
  if (row.rs_score == null) return null;
  return Math.max(0, Math.min(1, row.rs_score));
}

function scoreCvdLong(row: WatchRow): number | null {
  const st = row.cvd_state;
  if (st == null) return null;
  return ({ up: 1, flat: 0.55, down: 0.25, down_strong: 0 } as Record<string, number>)[st] ?? 0.55;
}

function scoreOiExpand(row: WatchRow): number | null {
  const st = row.oi_state;
  if (st == null) return null;
  return ({ up: 1, flat: 0.55, down: 0.25, collapse: 0 } as Record<string, number>)[st] ?? 0.55;
}

function scoreFundingOk(row: WatchRow): number | null {
  if (row.market !== "crypto") return null;
  if (row.funding == null) return null;
  const fr = row.funding;
  if (fr >= FUNDING_EXTREME) return 0;
  if (fr >= FUNDING_EXTREME * 0.5) return 0.4;
  if (fr <= -FUNDING_EXTREME) return 0.85;
  return 1;
}

function scoreRvol(row: WatchRow): number | null {
  if (row.rvol == null) return null;
  const high = PLAYBOOK_THRESHOLDS.rvol.high ?? RVOL_INTEREST;
  const low = PLAYBOOK_THRESHOLDS.rvol.low ?? 1.0;
  if (row.rvol >= high) return 1;
  if (row.rvol >= low) return 0.55;
  return 0.25;
}

const FNS: Record<string, (r: WatchRow) => number | null> = {
  tech: scoreTech,
  rs: scoreRs,
  cvd_long: scoreCvdLong,
  oi_expand: scoreOiExpand,
  funding_ok: scoreFundingOk,
  rvol: scoreRvol,
};

export function confluenceScore(
  row: WatchRow,
  weights: Record<string, number> = CONFLUENCE_WEIGHTS as unknown as Record<string, number>
): { score: number; breakdown: Record<string, Breakdown>; renorm: boolean } {
  const breakdown: Record<string, Breakdown> = {};
  const available: { name: string; weight: number; raw: number }[] = [];

  for (const [name, weight] of Object.entries(weights)) {
    const fn = FNS[name];
    const raw = fn ? fn(row) : null;
    if (raw == null) {
      breakdown[name] = { weight, raw: null, contrib: null, status: "n/d" };
      continue;
    }
    available.push({ name, weight, raw });
    breakdown[name] = { weight, raw: Math.round(raw * 10000) / 10000, contrib: null, status: "ok" };
  }

  if (!available.length) {
    return { score: 0, breakdown, renorm: true };
  }

  const wsum = available.reduce((a, x) => a + x.weight, 0);
  let score = 0;
  for (const { name, weight, raw } of available) {
    const nw = weight / wsum;
    const contrib = nw * raw * 100;
    breakdown[name].contrib = Math.round(contrib * 100) / 100;
    breakdown[name].weight_norm = Math.round(nw * 10000) / 10000;
    score += contrib;
  }

  return {
    score: Math.round(score * 10) / 10,
    breakdown,
    renorm: available.length < Object.keys(weights).length,
  };
}

export function attachConfluence(row: WatchRow): WatchRow {
  const r = confluenceScore(row);
  row.confluence = r.score;
  row.confluence_breakdown = r.breakdown;
  row.confluence_renorm = r.renorm;
  return row;
}

export function sortByConfluence(rows: WatchRow[]): WatchRow[] {
  for (const r of rows) {
    if (r.confluence == null) attachConfluence(r);
  }
  return [...rows].sort(
    (a, b) => (b.confluence ?? 0) - (a.confluence ?? 0) || (b.rs_score ?? 0) - (a.rs_score ?? 0)
  );
}
