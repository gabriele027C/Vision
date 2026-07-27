/**
 * Playbook condizionale (FASE 5-BIS) — speculare a engine/playbook.py.
 * Testi solo da assets/playbook.json. Trigger = stati FASE 4.
 */
import playbookJson from "../../assets/playbook.json";
import { FUNDING_EXTREME, PLAYBOOK_THRESHOLDS, RVOL_INTEREST } from "../config";
import type { WatchRow } from "./types";

export interface ScenarioCard {
  id: string;
  famiglia: string;
  titolo: string;
  trigger: Record<string, unknown>;
  lettura: string;
  monitorare: string[];
  invalidazione: string;
  errore_tipico: string;
  lato_operativo: boolean;
  footer: string;
}

export interface Playbook {
  version: number;
  note: string;
  scenari: ScenarioCard[];
  checklist_universali: Record<string, string[]>;
}

const REQUIRED = [
  "id",
  "famiglia",
  "titolo",
  "trigger",
  "lettura",
  "monitorare",
  "invalidazione",
  "errore_tipico",
  "lato_operativo",
  "footer",
] as const;

let _cache: Playbook | null = null;

export function loadPlaybook(data: Playbook = playbookJson as Playbook, force = false): Playbook {
  if (_cache && !force) return _cache;
  if (!Array.isArray(data.scenari)) throw new Error("playbook: manca lista scenari");
  data.scenari.forEach((card, i) => {
    for (const k of REQUIRED) {
      if (!(k in card)) throw new Error(`playbook scenari[${i}] manca ${k}`);
    }
  });
  if (!data.checklist_universali) throw new Error("playbook: manca checklist_universali");
  _cache = data;
  return data;
}

export function classifyFunding(funding: number | null | undefined, direction = "long"): string | null {
  if (funding == null) return null;
  if (direction === "long" && funding >= FUNDING_EXTREME) return "extreme_against_long";
  if (funding <= -FUNDING_EXTREME) return direction === "long" ? "negative" : "extreme_against_short";
  if (funding < 0) return "negative";
  if (funding > 0) return "positive";
  return "flat";
}

export function classifyRvol(rvol: number | null | undefined): string | null {
  if (rvol == null) return null;
  const high = PLAYBOOK_THRESHOLDS.rvol.high ?? RVOL_INTEREST;
  const low = PLAYBOOK_THRESHOLDS.rvol.low ?? 1.0;
  if (rvol >= high) return "high";
  if (rvol < low) return "low";
  return "normal";
}

export function buildAssetState(
  row: Partial<WatchRow>,
  flow?: Record<string, unknown> | null
): Record<string, unknown> {
  const state: Record<string, unknown> = {};
  const f = flow ?? {};
  const prezzo = f.price_state ?? (row as { price_state?: string }).price_state;
  if (prezzo) state.prezzo = prezzo;
  const oi = f.oi_state ?? row.oi_state;
  if (oi) state.oi = oi;
  const cvd = f.cvd_state ?? row.cvd_state;
  if (cvd) state.cvd = cvd;
  const fund = classifyFunding(row.funding ?? null, row.direction ?? "long");
  if (fund) state.funding = fund;
  const rv = classifyRvol(row.rvol ?? null);
  if (rv) state.rvol = rv;
  if (row.setup === "A") state.evento = "pullback";
  else if (row.setup === "B") state.evento = "breakout";
  const tf4 = row.tf_4h as { squeeze?: boolean } | undefined;
  if (
    tf4?.squeeze ||
    (row.setup === "B" && (row.entry_tf === "D" || row.entry_tf === "4H" || row.entry_tf == null))
  ) {
    state.squeeze_d_or_4h = true;
  }
  const timing = (row as { timing?: { timeframe?: string }[] }).timing ?? [];
  if (timing.some((t) => t.timeframe === "1H" || t.timeframe === "15m")) {
    state.squeeze_1h_or_15m = true;
  }
  if (row.direction === "long") state.trend = "up_aligned";
  else if (row.direction === "short" || (row as { bearish?: boolean }).bearish) {
    state.trend = "down_aligned";
  }
  if (row.rvol != null && Number(row.rvol) >= 3) state.volume = "extreme";
  if (state.oi === "collapse" && state.volume === "extreme") state.evento = "cascade";
  return state;
}

function triggerMatch(trigger: Record<string, unknown>, state: Record<string, unknown>): boolean {
  for (const [key, expected] of Object.entries(trigger)) {
    if (!(key in state)) return false;
    const actual = state[key];
    if (Array.isArray(expected)) {
      if (!expected.includes(actual)) return false;
    } else if (typeof expected === "boolean") {
      if (Boolean(actual) !== expected) return false;
    } else if (actual !== expected) {
      return false;
    }
  }
  return true;
}

export function activeScenarios(
  assetState: Record<string, unknown>,
  playbook?: Playbook
): ScenarioCard[] {
  const pb = playbook ?? loadPlaybook();
  const matched = pb.scenari.filter((c) => triggerMatch(c.trigger, assetState));
  matched.sort((a, b) => Number(a.lato_operativo) - Number(b.lato_operativo) || a.id.localeCompare(b.id));
  return matched;
}

export function scenarioIdsForRow(row: WatchRow, flow?: Record<string, unknown> | null): string[] {
  return activeScenarios(buildAssetState(row, flow)).map((c) => c.id);
}

export function primaryAlertScenario(row: WatchRow, flow?: Record<string, unknown> | null): ScenarioCard | null {
  for (const c of activeScenarios(buildAssetState(row, flow))) {
    if (c.lato_operativo) return c;
  }
  return null;
}

export function universalChecklist(name = "pre_ingresso"): string[] {
  return [...(loadPlaybook().checklist_universali[name] ?? [])];
}
