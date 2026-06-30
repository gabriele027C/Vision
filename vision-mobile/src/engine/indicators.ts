/** Indicatori base — Wilder per RSI/ATR, EMA standard per ema(). */

function ewmAlpha(series: number[], alpha: number): number[] {
  if (series.length === 0) return [];
  const out = new Array<number>(series.length);
  out[0] = series[0];
  for (let i = 1; i < series.length; i++) {
    out[i] = alpha * series[i] + (1 - alpha) * out[i - 1];
  }
  return out;
}

/** EMA standard: span → alpha = 2/(length+1), adjust=False */
export function ema(series: number[], length: number): number[] {
  if (series.length === 0) return [];
  const alpha = 2 / (length + 1);
  return ewmAlpha(series, alpha);
}

/** RSI Wilder: alpha = 1/length */
export function rsi(close: number[], length = 14): number[] {
  if (close.length < 2) return close.map(() => NaN);
  const gains = new Array<number>(close.length).fill(0);
  const losses = new Array<number>(close.length).fill(0);
  for (let i = 1; i < close.length; i++) {
    const d = close[i] - close[i - 1];
    gains[i] = d > 0 ? d : 0;
    losses[i] = d < 0 ? -d : 0;
  }
  const alpha = 1 / length;
  const avgGain = ewmAlpha(gains, alpha);
  const avgLoss = ewmAlpha(losses, alpha);
  return close.map((_, i) => {
    if (i === 0) return NaN;
    const loss = avgLoss[i];
    if (loss === 0) return 100;
    const rs = avgGain[i] / loss;
    return 100 - 100 / (1 + rs);
  });
}

/** ATR Wilder su true range */
export function atr(
  high: number[],
  low: number[],
  close: number[],
  length = 14
): number[] {
  const tr = close.map((_, i) => {
    if (i === 0) return high[i] - low[i];
    const prev = close[i - 1];
    return Math.max(
      high[i] - low[i],
      Math.abs(high[i] - prev),
      Math.abs(low[i] - prev)
    );
  });
  return ewmAlpha(tr, 1 / length);
}

export function bollingerWidth(close: number[], length = 20, mult = 2.0): number[] {
  const out = new Array<number>(close.length).fill(NaN);
  for (let i = length - 1; i < close.length; i++) {
    const slice = close.slice(i - length + 1, i + 1);
    const mid = slice.reduce((a, b) => a + b, 0) / length;
    const variance = slice.reduce((s, v) => s + (v - mid) ** 2, 0) / length;
    const std = Math.sqrt(variance);
    out[i] = mid !== 0 ? (2 * mult * std) / mid : NaN;
  }
  return out;
}

/** Volume / media volume 20 giorni precedenti (esclude il giorno stesso) */
export function rvol(volume: number[], length = 20): number[] {
  const out = new Array<number>(volume.length).fill(NaN);
  for (let i = length; i < volume.length; i++) {
    const prev = volume.slice(i - length, i);
    const mean = prev.reduce((a, b) => a + b, 0) / length;
    out[i] = mean > 0 ? volume[i] / mean : NaN;
  }
  return out;
}

export function adrPct(high: number[], low: number[], length = 20): number {
  if (high.length < length) return 0;
  const rng = high.map((h, i) => (h / low[i] - 1) * 100);
  const slice = rng.slice(-length);
  const val = slice.reduce((a, b) => a + b, 0) / length;
  return Number.isFinite(val) ? val : 0;
}

export function pctReturn(close: number[], periods: number): number {
  if (close.length <= periods) return 0;
  const last = close[close.length - 1];
  const prev = close[close.length - 1 - periods];
  return last / prev - 1;
}
