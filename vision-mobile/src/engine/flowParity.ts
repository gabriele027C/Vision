/**
 * Parità col motore Python (test_flow_parity.py) su dati sintetici.
 * Stessi input → stessi stati/frecce.
 */
import {
  buildFlowSnapshot,
  classifyCvd,
  classifyOi,
  cvdSlopeNormalized,
  oiDeltasFromHist,
} from "./flow";

const OI_CASES: [number, string][] = [
  [0.06, "up"],
  [0.05, "up"],
  [0.049, "flat"],
  [-0.05, "down"],
  [-0.19, "down"],
  [-0.2, "collapse"],
  [-0.25, "collapse"],
];

const CVD_CASES: [number, string][] = [
  [0.03, "up"],
  [0.02, "up"],
  [0.0, "flat"],
  [-0.02, "down"],
  [-0.05, "down"],
  [-0.06, "down_strong"],
];

export function runFlowParityChecks(): string[] {
  const errors: string[] = [];
  for (const [d, exp] of OI_CASES) {
    const got = classifyOi(d);
    if (got !== exp) errors.push(`OI ${d}: got ${got} expected ${exp}`);
  }
  for (const [s, exp] of CVD_CASES) {
    const got = classifyCvd(s);
    if (got !== exp) errors.push(`CVD ${s}: got ${got} expected ${exp}`);
  }

  const oiVals = Array(18).fill(100).concat([112]);
  const deltas = oiDeltasFromHist(oiVals, 6);
  if (classifyOi(deltas.oi_delta_24h) !== "up") {
    errors.push(`oi_delta_24h state: ${classifyOi(deltas.oi_delta_24h)}`);
  }

  const n = 20;
  const vol = Array(n).fill(1000);
  const tbbUp = vol.map((v) => v * 0.75);
  const slopeUp = cvdSlopeNormalized(vol, tbbUp);
  if (classifyCvd(slopeUp) !== "up") {
    errors.push(`slope_up state: ${classifyCvd(slopeUp)} slope=${slopeUp}`);
  }

  const snap = buildFlowSnapshot({
    oi_value: deltas.oi_value,
    oi_delta_24h: deltas.oi_delta_24h,
    oi_delta_3d: deltas.oi_delta_3d,
    cvd_slope: slopeUp,
    price_delta: 0.02,
  });
  if (snap.oi_arrow !== "↑") errors.push(`oi_arrow ${snap.oi_arrow}`);
  if (snap.cvd_arrow !== "↑") errors.push(`cvd_arrow ${snap.cvd_arrow}`);
  if (snap.price_state !== "up") errors.push(`price_state ${snap.price_state}`);

  return errors;
}
