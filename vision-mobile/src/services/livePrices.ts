/** Prezzi live + coerenza status/rottura — speculare a services/live_prices.py. */
import * as binanceClient from "../data/binanceClient";
import * as stocksClient from "../data/stocksClient";
import type { WatchRow } from "../engine/types";

const PRICE_REFRESH_TTL_S = 20;

export function reconcileStatusWithPrice(row: WatchRow): void {
  if (row.status === "blocked") return;
  const px = row.last_price;
  const trig = row.entry_trigger;
  if (px == null || trig == null || Number.isNaN(px) || Number.isNaN(trig)) return;

  if (row.direction === "long") {
    if (row.status === "triggered" && px < trig) {
      row.status = px >= trig * 0.99 ? "near" : "watch";
      const warn =
        "Prezzo live sotto rottura: stato riallineato (triggered era su close 4H)";
      if (!row.warnings.includes(warn)) row.warnings.push(warn);
    } else if (row.status === "watch" && px >= trig * 0.99) {
      row.status = "near";
    }
  } else {
    if (row.status === "triggered" && px > trig) {
      row.status = px <= trig * 1.01 ? "near" : "watch";
      const warn =
        "Prezzo live sopra rottura short: stato riallineato (triggered era su close 4H)";
      if (!row.warnings.includes(warn)) row.warnings.push(warn);
    } else if (row.status === "watch" && px <= trig * 1.01) {
      row.status = "near";
    }
  }
}

function roundPrice(px: number): number {
  return px < 1 ? Math.round(px * 1e6) / 1e6 : Math.round(px * 1e4) / 1e4;
}

export function applyLivePrices(
  rows: WatchRow[],
  prices: Record<string, number>,
  asof?: string
): number {
  const ts = asof ?? new Date().toISOString().replace(/\.\d{3}Z$/, "+00:00");
  let n = 0;
  for (const row of rows) {
    const px = prices[row.symbol];
    if (px == null) continue;
    row.last_price = roundPrice(px);
    row.price_live = true;
    row.price_asof = ts;
    reconcileStatusWithPrice(row);
    n += 1;
  }
  return n;
}

export async function fetchLivePrices(
  cryptoSyms: string[],
  stockSyms: string[]
): Promise<Record<string, number>> {
  const prices: Record<string, number> = {};
  if (cryptoSyms.length) Object.assign(prices, await binanceClient.lastPrices(cryptoSyms));
  if (stockSyms.length) Object.assign(prices, await stocksClient.lastPrices(stockSyms));
  return prices;
}

/** Imposta last_price al prezzo di mercato corrente (fine scan).
 *  Crypto → futures USDT-M; stocks → Yahoo. */
export async function stampLivePrices(
  rows: WatchRow[],
  market: "crypto" | "stocks"
): Promise<number> {
  if (!rows.length) return 0;
  const syms = rows.map((r) => r.symbol).filter(Boolean);
  const prices =
    market === "crypto"
      ? await fetchLivePrices(syms, [])
      : await fetchLivePrices([], syms);
  return applyLivePrices(rows, prices);
}

export class PriceRefreshGate {
  private last = 0;
  constructor(private ttlS = PRICE_REFRESH_TTL_S) {}

  allow(force = false): boolean {
    const now = Date.now() / 1000;
    if (force) {
      this.last = now;
      return true;
    }
    if (now - this.last < this.ttlS) return false;
    this.last = now;
    return true;
  }
}
