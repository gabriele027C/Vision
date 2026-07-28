import * as Linking from "expo-linking";

/** Formato prezzi stile trading: punto decimale, niente separatore migliaia italiano.
 *  Evita che 64841 diventi "64.841,8" (leggibile come ~64.8 vs chart futures). */
export function fmt(x: number): string {
  if (x == null || Number.isNaN(x)) return "—";
  const ax = Math.abs(x);
  if (ax >= 1000) return x.toFixed(2);
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
