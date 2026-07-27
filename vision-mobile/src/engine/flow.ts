/**
 * OI + CVD: classificazione descrittiva (FASE 4).
 * Speculare a engine/flow.py — stesse soglie PLAYBOOK_THRESHOLDS.
 */
import { PLAYBOOK_THRESHOLDS } from "../config";

export type OiState = "up" | "down" | "flat" | "collapse";
export type CvdState = "up" | "down" | "flat" | "down_strong";
export type PriceState = "up" | "down" | "flat";

export const STATE_ARROW: Record<string, string> = {
  up: "↑",
  down: "↓",
  flat: "→",
  collapse: "↓↓",
  down_strong: "↓↓",
};

export function classifyOi(delta24h: number | null | undefined): OiState | null {
  if (delta24h == null || !Number.isFinite(delta24h)) return null;
  const thr = PLAYBOOK_THRESHOLDS.oi;
  if (delta24h <= thr.collapse_pct_24h) return "collapse";
  if (delta24h >= thr.up_pct_24h) return "up";
  if (delta24h <= thr.down_pct_24h) return "down";
  return "flat";
}

export function classifyCvd(slopeNorm: number | null | undefined): CvdState | null {
  if (slopeNorm == null || !Number.isFinite(slopeNorm)) return null;
  const thr = PLAYBOOK_THRESHOLDS.cvd;
  if (slopeNorm <= thr.down_strong) return "down_strong";
  if (slopeNorm >= thr.up) return "up";
  if (slopeNorm <= thr.down) return "down";
  return "flat";
}

export function classifyPrice(
  deltaPct: number | null | undefined,
  flatBand = 0.005
): PriceState | null {
  if (deltaPct == null || !Number.isFinite(deltaPct)) return null;
  if (deltaPct >= flatBand) return "up";
  if (deltaPct <= -flatBand) return "down";
  return "flat";
}

export function oiDeltasFromHist(
  oiValues: number[],
  barsPerDay = 6
): { oi_value: number | null; oi_delta_24h: number | null; oi_delta_3d: number | null } {
  if (!oiValues.length) {
    return { oi_value: null, oi_delta_24h: null, oi_delta_3d: null };
  }
  const last = oiValues[oiValues.length - 1];
  const out = {
    oi_value: last,
    oi_delta_24h: null as number | null,
    oi_delta_3d: null as number | null,
  };
  if (!(last > 0)) return out;
  const i24 = barsPerDay;
  const i3d = barsPerDay * 3;
  if (oiValues.length > i24) {
    const prev = oiValues[oiValues.length - 1 - i24];
    if (prev > 0) out.oi_delta_24h = (last - prev) / prev;
  }
  if (oiValues.length > i3d) {
    const prev = oiValues[oiValues.length - 1 - i3d];
    if (prev > 0) out.oi_delta_3d = (last - prev) / prev;
  }
  return out;
}

export function barDelta(volume: number, takerBuy: number): number {
  return 2 * takerBuy - volume;
}

export function cvdSeries(volume: number[], takerBuy: number[]): number[] {
  const out: number[] = [];
  let cum = 0;
  for (let i = 0; i < volume.length; i++) {
    cum += 2 * takerBuy[i] - volume[i];
    out.push(cum);
  }
  return out;
}

export function cvdSlopeNormalized(
  volume: number[],
  takerBuy: number[],
  bars?: number
): number | null {
  const n = bars ?? PLAYBOOK_THRESHOLDS.cvd.slope_bars;
  if (volume.length < n || takerBuy.length < n) return null;
  const v = volume.slice(-n);
  const t = takerBuy.slice(-n);
  const cvd = cvdSeries(v, t);
  const meanVol = v.reduce((a, b) => a + b, 0) / n;
  if (!(meanVol > 0)) return null;
  let xMean = 0;
  for (let i = 0; i < n; i++) xMean += i;
  xMean /= n;
  let yMean = 0;
  for (const y of cvd) yMean += y;
  yMean /= n;
  let varX = 0;
  let cov = 0;
  for (let i = 0; i < n; i++) {
    const dx = i - xMean;
    varX += dx * dx;
    cov += dx * (cvd[i] - yMean);
  }
  if (varX <= 0) return null;
  return cov / varX / meanVol;
}

export function priceDeltaPct(close: number[], lookback = 6): number | null {
  if (close.length <= lookback) return null;
  const prev = close[close.length - 1 - lookback];
  if (!(prev > 0)) return null;
  return (close[close.length - 1] - prev) / prev;
}

export function describeCombo(
  price: PriceState | null,
  oi: OiState | null,
  cvd: CvdState | null
): { combo_key: string; label: string; message: string } {
  const key = `price_${price ?? "na"}|oi_${oi ?? "na"}|cvd_${cvd ?? "na"}`;
  if (price == null && oi == null && cvd == null) {
    return {
      combo_key: key,
      label: "flusso non disponibile",
      message: "OI/CVD non calcolabili per questo asset",
    };
  }
  const parts: string[] = [];
  if (price === "up") parts.push("prezzo↑");
  else if (price === "down") parts.push("prezzo↓");
  else if (price === "flat") parts.push("prezzo→");
  if (oi === "up") parts.push("OI↑");
  else if (oi === "down") parts.push("OI↓");
  else if (oi === "collapse") parts.push("OI collapse");
  else if (oi === "flat") parts.push("OI→");
  if (cvd === "up") parts.push("CVD↑");
  else if (cvd === "down") parts.push("CVD↓");
  else if (cvd === "down_strong") parts.push("CVD↓↓");
  else if (cvd === "flat") parts.push("CVD→");

  const label = parts.length ? parts.join(" + ") : "flusso parziale";
  let message: string;
  if (price === "up" && oi === "up" && cvd === "up") {
    message =
      "Partecipazione in aumento col prezzo (nuovi aggressori in acquisto) — descrittivo.";
  } else if (price === "up" && oi === "down") {
    message = "Prezzo↑ con OI↓: tipico short covering — base potenzialmente fragile.";
  } else if (
    price === "up" &&
    (oi === "flat" || oi == null) &&
    (cvd === "flat" || cvd === "down" || cvd === "down_strong" || cvd == null)
  ) {
    message = "Prezzo↑ senza conferma aggressori — trend sottile o esausto.";
  } else if (oi === "collapse") {
    message = "OI in collasso (−20%+ /24h): deleveraging / liquidazioni in corso.";
  } else if (cvd === "down_strong" && price === "up") {
    message = "Prezzo↑ ma CVD fortemente negativo: possibile distribuzione.";
  } else if (price === "down" && oi === "up" && (cvd === "down" || cvd === "down_strong")) {
    message = "Prezzo↓ + OI↑ + CVD↓: nuovi short / pressione in vendita.";
  } else {
    message =
      "Combinazione mista — confronta col grafico; nessuna inferenza automatica.";
  }
  return { combo_key: key, label, message };
}

export interface FlowSnapshot {
  oi_value: number | null;
  oi_delta_24h: number | null;
  oi_delta_3d: number | null;
  oi_state: OiState | null;
  oi_arrow: string | null;
  cvd_slope: number | null;
  cvd_state: CvdState | null;
  cvd_arrow: string | null;
  price_state: PriceState | null;
  combo_key: string;
  combo_label: string;
  combo_message: string;
}

export function buildFlowSnapshot(opts: {
  oi_value?: number | null;
  oi_delta_24h?: number | null;
  oi_delta_3d?: number | null;
  cvd_slope?: number | null;
  price_delta?: number | null;
}): FlowSnapshot {
  const oiState = classifyOi(opts.oi_delta_24h ?? null);
  const cvdState = classifyCvd(opts.cvd_slope ?? null);
  const priceState = classifyPrice(opts.price_delta ?? null);
  const combo = describeCombo(priceState, oiState, cvdState);
  const round6 = (x: number | null | undefined) =>
    x == null ? null : Math.round(x * 1e6) / 1e6;
  return {
    oi_value: opts.oi_value ?? null,
    oi_delta_24h: round6(opts.oi_delta_24h),
    oi_delta_3d: round6(opts.oi_delta_3d),
    oi_state: oiState,
    oi_arrow: oiState ? STATE_ARROW[oiState] : null,
    cvd_slope: round6(opts.cvd_slope),
    cvd_state: cvdState,
    cvd_arrow: cvdState ? STATE_ARROW[cvdState] : null,
    price_state: priceState,
    combo_key: combo.combo_key,
    combo_label: combo.label,
    combo_message: combo.message,
  };
}
