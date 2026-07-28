import * as Linking from "expo-linking";

/** Formato prezzi stile trading: punto decimale, migliaia en-US (≥1000).
 *  Evita notazione scientifica e locale IT (64.841,8). */
export function fmt(x: number): string {
  if (x == null || Number.isNaN(x)) return "—";
  const ax = Math.abs(x);
  if (ax >= 1000) {
    return x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  if (ax >= 1) return x.toFixed(2);
  if (ax >= 0.01) return x.toFixed(4);
  return x.toPrecision(4);
}

export function tvUrl(market: string, symbol: string): string {
  // Crypto: perpetual Binance (allineato a PREZZO futures / OI / funding)
  const tvSymbol =
    market === "crypto" ? `BINANCE:${symbol}.P` : symbol.replace("-", ".");
  return `https://www.tradingview.com/chart/?symbol=${encodeURIComponent(tvSymbol)}&interval=D`;
}

export function openTradingView(market: string, symbol: string): void {
  Linking.openURL(tvUrl(market, symbol));
}
