import { VIX_HALT } from "../config";
import type { OHLCVBar, Regime } from "./types";
import { ema } from "./indicators";

function trend(bars: OHLCVBar[]): "up" | "down" | "mixed" {
  const close = bars.map((b) => b.close);
  const e50 = ema(close, 50);
  const e200 = ema(close, 200);
  const last = close[close.length - 1];
  const slopeUp = e50[e50.length - 1] > e50[e50.length - 6];
  if (last > e200[e200.length - 1] && slopeUp) return "up";
  if (last < e200[e200.length - 1] && !slopeUp) return "down";
  return "mixed";
}

export function stockRegime(
  spy: OHLCVBar[],
  qqq: OHLCVBar[],
  vixLast: number | null
): Regime {
  const tSpy = trend(spy);
  const tQqq = trend(qqq);
  let mode: Regime["mode"];
  if (vixLast !== null && vixLast > VIX_HALT) {
    mode = "halt";
  } else if (tSpy === "up" && tQqq === "up") {
    mode = "long";
  } else if (tSpy === "down" && tQqq === "down") {
    mode = "short";
  } else {
    mode = "mixed";
  }
  return {
    market: "stocks",
    mode,
    long_allowed: mode === "long" || mode === "mixed",
    short_allowed: mode === "short" || mode === "mixed",
    half_size: mode === "mixed",
    detail: { SPY: tSpy, QQQ: tQqq, VIX: vixLast },
  };
}

export function cryptoRegime(btc: OHLCVBar[]): Regime {
  const close = btc.map((b) => b.close);
  const e50 = ema(close, 50);
  const e200 = ema(close, 200);
  const last = close[close.length - 1];
  let mode: Regime["mode"];
  if (last > e200[e200.length - 1] && last > e50[e50.length - 1]) {
    mode = "long";
  } else if (last < e200[e200.length - 1] && last < e50[e50.length - 1]) {
    mode = "short";
  } else {
    mode = "mixed";
  }
  return {
    market: "crypto",
    mode,
    long_allowed: mode === "long" || mode === "mixed",
    short_allowed: mode === "short" || mode === "mixed",
    half_size: mode === "mixed",
    detail: {
      BTC_vs_EMA200: last > e200[e200.length - 1] ? "above" : "below",
      BTC_vs_EMA50: last > e50[e50.length - 1] ? "above" : "below",
    },
  };
}
