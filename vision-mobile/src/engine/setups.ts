/** Rilevamento Setup A (pullback in trend) e Setup B (breakout da compressione).
 *
 * Implementazione fedele a docs/STRATEGIA_SWING.md §4-§6.
 */
import { MARKET_PARAMS, MAX_STOP_ATR, RVOL_BREAKOUT, type MarketParams } from "../config";
import { atr, bollingerWidth, ema, rsi, rvol } from "./indicators";
import type { OHLCVBar } from "./types";

export const SQUEEZE_LOOKBACK = 60;
export const RANGE_BARS = 15;

// Fallback storici (market assente): stessi valori usati prima della Fase 5.
const DEFAULT_PARAMS: MarketParams = {
  RANGE_BARS,
  SQUEEZE_LOOKBACK,
  RSI_LONG_MIN: 40,
  RSI_SHORT_MAX: 60,
};

export function marketParams(market?: "crypto" | "stocks" | null): MarketParams {
  if (market && MARKET_PARAMS[market]) {
    return { ...DEFAULT_PARAMS, ...MARKET_PARAMS[market] };
  }
  return DEFAULT_PARAMS;
}

function roundPx(x: number): number {
  return parseFloat(x.toPrecision(6));
}

function rollingMean(arr: number[], window: number): number[] {
  const out = new Array<number>(arr.length).fill(NaN);
  for (let i = window - 1; i < arr.length; i++) {
    const slice = arr.slice(i - window + 1, i + 1);
    out[i] = slice.reduce((a, b) => a + b, 0) / window;
  }
  return out;
}

function rollingMin(arr: number[], window: number): number[] {
  const out = new Array<number>(arr.length).fill(NaN);
  for (let i = window - 1; i < arr.length; i++) {
    out[i] = Math.min(...arr.slice(i - window + 1, i + 1));
  }
  return out;
}

function rollingMax(arr: number[], window: number): number[] {
  const out = new Array<number>(arr.length).fill(NaN);
  for (let i = window - 1; i < arr.length; i++) {
    out[i] = Math.max(...arr.slice(i - window + 1, i + 1));
  }
  return out;
}

function quantile(arr: number[], q: number): number {
  const sorted = [...arr].filter((v) => Number.isFinite(v)).sort((a, b) => a - b);
  if (!sorted.length) return NaN;
  const pos = (sorted.length - 1) * q;
  const lo = Math.floor(pos);
  const hi = Math.ceil(pos);
  if (lo === hi) return sorted[lo];
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo);
}

function ohlcvCols(bars: OHLCVBar[]) {
  return {
    open: bars.map((b) => b.open),
    high: bars.map((b) => b.high),
    low: bars.map((b) => b.low),
    close: bars.map((b) => b.close),
    volume: bars.map((b) => b.volume),
  };
}

export interface SetupAMetrics {
  aligned: boolean;
  in_zone: boolean;
  momentum_ok: boolean;
  vol_declining: boolean;
  stop_geometry_ok: boolean;
  rsi: number;
  atr: number;
  trigger: number;
  stop: number;
  stop_dist: number;
  vol5: number;
  vol20: number;
}

export function setupAMetrics(
  bars: OHLCVBar[],
  direction: string,
  market?: "crypto" | "stocks" | null
): SetupAMetrics | null {
  if (bars.length < 220) return null;
  const p = marketParams(market);

  const { high, low, close, volume } = ohlcvCols(bars);
  const e20 = ema(close, 20);
  const e50 = ema(close, 50);
  const e200 = ema(close, 200);
  const atrSeries = atr(high, low, close);
  const rsiSeries = rsi(close);
  const a = atrSeries[atrSeries.length - 1];
  const r = rsiSeries[rsiSeries.length - 1];
  const last = close[close.length - 1];
  const vol5Series = rollingMean(volume, 5);
  const vol20Series = rollingMean(volume, 20);
  const vol5 = vol5Series[vol5Series.length - 1];
  const vol20 = vol20Series[vol20Series.length - 1];
  const volDeclining = vol5 < vol20;

  let aligned: boolean;
  let inZone: boolean;
  let momentumOk: boolean;
  let swing: number;
  let stop: number;
  let trigger: number;

  if (direction === "long") {
    aligned =
      e20[e20.length - 1] > e50[e50.length - 1] &&
      e50[e50.length - 1] > e200[e200.length - 1] &&
      e50[e50.length - 1] > e50[e50.length - 6];
    inZone = e50[e50.length - 1] - 0.5 * a <= last && last <= e20[e20.length - 1] + 0.25 * a;
    momentumOk = r > p.RSI_LONG_MIN;
    const swingSeries = rollingMin(low, 10);
    swing = swingSeries[swingSeries.length - 1];
    stop = swing - 0.5 * a;
    trigger = Math.max(high[high.length - 2], high[high.length - 1]);
  } else {
    aligned =
      e20[e20.length - 1] < e50[e50.length - 1] &&
      e50[e50.length - 1] < e200[e200.length - 1] &&
      e50[e50.length - 1] < e50[e50.length - 6];
    inZone = e20[e20.length - 1] - 0.25 * a <= last && last <= e50[e50.length - 1] + 0.5 * a;
    momentumOk = r < p.RSI_SHORT_MAX;
    const swingSeries = rollingMax(high, 10);
    swing = swingSeries[swingSeries.length - 1];
    stop = swing + 0.5 * a;
    trigger = Math.min(low[low.length - 2], low[low.length - 1]);
  }

  const stopDist = Math.abs(trigger - stop);
  const stopGeometryOk = stopDist <= MAX_STOP_ATR * a;

  return {
    aligned,
    in_zone: inZone,
    momentum_ok: momentumOk,
    vol_declining: volDeclining,
    stop_geometry_ok: stopGeometryOk,
    rsi: r,
    atr: a,
    trigger,
    stop,
    stop_dist: stopDist,
    vol5,
    vol20,
  };
}

export interface SetupBMetrics {
  squeeze: boolean;
  context_ok: boolean;
  stop_geometry_ok: boolean;
  breakout_triggered: boolean;
  bbw_last: number;
  bbw_thresh: number;
  atr: number;
  trigger: number;
  stop: number;
  stop_dist: number;
  rvol: number;
  e200: number;
  last: number;
}

export function setupBMetrics(
  bars: OHLCVBar[],
  direction: string,
  market?: "crypto" | "stocks" | null
): SetupBMetrics | null {
  if (bars.length < 220) return null;
  const p = marketParams(market);

  const { high, low, close, volume } = ohlcvCols(bars);
  const e200Series = ema(close, 200);
  const e200 = e200Series[e200Series.length - 1];
  const last = close[close.length - 1];
  const atrSeries = atr(high, low, close);
  const a = atrSeries[atrSeries.length - 1];

  const bbw = bollingerWidth(close);
  const bbwLast = bbw[bbw.length - 1];
  // Quantile sulle barre PRECEDENTI la corrente — speculare a setups.py.
  const bbwSlice = bbw.slice(-p.SQUEEZE_LOOKBACK - 1, -1);
  const bbwThresh = quantile(bbwSlice, 0.1);
  const squeeze = bbwLast <= bbwThresh;

  // Il range di compressione esclude la barra corrente: includerla rendeva
  // impossibile close > rangeHigh (close <= high), quindi breakout_triggered
  // era sempre false (codice morto). Speculare al fix nel backend Python.
  const rangeHigh = Math.max(...high.slice(-p.RANGE_BARS - 1, -1));
  const rangeLow = Math.min(...low.slice(-p.RANGE_BARS - 1, -1));

  let contextOk: boolean;
  let trigger: number;
  let stop: number;

  if (direction === "long") {
    contextOk = last >= e200;
    trigger = rangeHigh;
    stop = Math.max(trigger - a, rangeLow);
  } else {
    contextOk = last <= e200;
    trigger = rangeLow;
    stop = Math.min(trigger + a, rangeHigh);
  }

  const stopDist = Math.abs(trigger - stop);
  const stopGeometryOk = stopDist <= MAX_STOP_ATR * a;

  const rvSeries = rvol(volume);
  const rvVal = rvSeries[rvSeries.length - 1];
  const rv = rvVal != null && !Number.isNaN(rvVal) ? rvVal : 0;
  const triggered =
    (direction === "long" && last > trigger && rv >= RVOL_BREAKOUT) ||
    (direction === "short" && last < trigger && rv >= RVOL_BREAKOUT);

  return {
    squeeze,
    context_ok: contextOk,
    stop_geometry_ok: stopGeometryOk,
    breakout_triggered: triggered,
    bbw_last: bbwLast,
    bbw_thresh: bbwThresh,
    atr: a,
    trigger,
    stop,
    stop_dist: stopDist,
    rvol: rv,
    e200,
    last,
  };
}

export interface SetupSignal {
  setup: "A" | "B";
  direction: string;
  entry_trigger: number;
  stop: number;
  atr: number;
  rsi?: number;
  status_hint?: "triggered" | "watch";
  note: string;
}

export function detectSetupA(
  bars: OHLCVBar[],
  direction: string,
  market?: "crypto" | "stocks" | null
): SetupSignal | null {
  const m = setupAMetrics(bars, direction, market);
  if (m == null) return null;
  if (!(m.aligned && m.in_zone && m.vol_declining)) return null;
  if (!m.stop_geometry_ok) return null;

  return {
    setup: "A",
    direction,
    entry_trigger: roundPx(m.trigger),
    stop: roundPx(m.stop),
    atr: roundPx(m.atr),
    rsi: Math.round(m.rsi * 10) / 10,
    note: "Pullback in trend: verifica chiusura oltre il livello di rottura su 4H con volume (TradingView)",
  };
}

export function detectSetupB(
  bars: OHLCVBar[],
  direction: string,
  market?: "crypto" | "stocks" | null
): SetupSignal | null {
  const m = setupBMetrics(bars, direction, market);
  if (m == null) return null;
  if (!m.squeeze) return null;
  if (!m.context_ok) return null;
  if (!m.stop_geometry_ok) return null;

  return {
    setup: "B",
    direction,
    entry_trigger: roundPx(m.trigger),
    stop: roundPx(m.stop),
    atr: roundPx(m.atr),
    status_hint: m.breakout_triggered ? "triggered" : "watch",
    note: `Breakout da squeeze: serve chiusura daily oltre il livello con RVOL>=${RVOL_BREAKOUT}`,
  };
}

export function triggerStatus4h(
  bars4h: OHLCVBar[],
  direction: string,
  trigger: number
): "triggered" | "near" | "watch" {
  if (!bars4h.length || bars4h.length < 25) return "watch";

  const lastClose = bars4h[bars4h.length - 1].close;
  const vol = bars4h.map((b) => b.volume);
  // Media delle 20 barre precedenti (equivalente a shift(1) in pandas).
  const volMean = rollingMean(vol, 20);
  const volOk = vol[vol.length - 1] > volMean[volMean.length - 2];

  if (direction === "long") {
    if (lastClose > trigger && volOk) return "triggered";
    if (lastClose >= trigger * 0.99) return "near";
  } else {
    if (lastClose < trigger && volOk) return "triggered";
    if (lastClose <= trigger * 1.01) return "near";
  }
  return "watch";
}
