import * as Linking from "expo-linking";

export function fmt(x: number): string {
  if (x >= 1000) return x.toLocaleString("it-IT", { maximumFractionDigits: 2 });
  if (x >= 1) return x.toFixed(2);
  return x.toPrecision(4);
}

export function tvUrl(market: string, symbol: string): string {
  const tvSymbol = market === "crypto" ? `BINANCE:${symbol}` : symbol.replace("-", ".");
  return `https://www.tradingview.com/chart/?symbol=${encodeURIComponent(tvSymbol)}&interval=D`;
}

export function openTradingView(market: string, symbol: string): void {
  Linking.openURL(tvUrl(market, symbol));
}
