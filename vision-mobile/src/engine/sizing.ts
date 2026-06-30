import type { SizingResult } from "./types";

export function positionSize(
  capital: number,
  riskPct: number,
  entry: number,
  stop: number,
  halfSize = false
): SizingResult {
  let riskAmount = capital * (riskPct / 100);
  if (halfSize) riskAmount /= 2;
  const distance = Math.abs(entry - stop);
  if (distance <= 0 || entry <= 0) {
    return { error: "Entrata e stop non validi (distanza nulla)" };
  }
  const sizeUnits = riskAmount / distance;
  const notional = sizeUnits * entry;
  return {
    risk_amount: Math.round(riskAmount * 100) / 100,
    stop_distance: Math.round(distance * 1e6) / 1e6,
    stop_distance_pct: Math.round((distance / entry) * 100 * 100) / 100,
    size_units: Math.round(sizeUnits * 1e6) / 1e6,
    notional: Math.round(notional * 100) / 100,
    half_size: halfSize,
    target_2r_long: Math.round((entry + 2 * distance) * 1e6) / 1e6,
    target_2r_short: Math.round((entry - 2 * distance) * 1e6) / 1e6,
  };
}
