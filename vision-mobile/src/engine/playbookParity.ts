/**
 * Parità col motore Python (test_playbook_parity.py) su stati sintetici.
 */
import { activeScenarios, loadPlaybook } from "./playbook";

const PARITY_STATES: Record<string, unknown>[] = [
  { prezzo: "up", oi: "up", cvd: "up" },
  { prezzo: "up", oi: "down" },
  { prezzo: "up", oi: "flat", cvd: "down" },
  { funding: "extreme_against_long" },
  { funding: "negative", prezzo: "up" },
  { evento: "breakout", rvol: "high" },
  { squeeze_d_or_4h: true, squeeze_1h_or_15m: true },
  { trend: "down_aligned" },
  { evento: "cascade", oi: "collapse", volume: "extreme" },
  { prezzo: "up" },
];

export function runPlaybookParityChecks(): string[] {
  loadPlaybook(undefined, true);
  const errors: string[] = [];
  const results = PARITY_STATES.map((s) => activeScenarios(s).map((c) => c.id));
  if (!results.some((r) => r.length)) errors.push("nessuno scenario attivato");
  if (!results[0].includes("trend_nuovi_aggressori")) errors.push("manca trend_nuovi_aggressori");
  if (!results[1].includes("short_covering")) errors.push("manca short_covering");
  if (!results[3].includes("carry_avverso")) errors.push("manca carry_avverso");
  if (!results[7].includes("contesto_ribassista")) errors.push("manca contesto_ribassista");
  if (!results[8].includes("capitolazione")) errors.push("manca capitolazione");
  if (results[9].includes("short_covering")) errors.push("short_covering non dovrebbe attivarsi senza oi");
  return errors;
}
