/** Client API pubblica Binance (spot + funding futures). Nessuna API key richiesta. */
import {
  CRYPTO_TOP_N,
  LEVERAGED_SUFFIXES,
  MIN_CRYPTO_QUOTE_VOLUME,
  STABLECOINS,
} from "../config";
import type { OHLCVBar } from "../engine/types";

const SPOT = "https://api.binance.com";
const FUTURES = "https://fapi.binance.com";
const TIMEOUT_MS = 20_000;

async function get<T>(url: string, params?: Record<string, string | number>): Promise<T> {
  const qs = params
    ? "?" + new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)])).toString()
    : "";
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    const resp = await fetch(url + qs, { signal: ctrl.signal });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${url}`);
    return (await resp.json()) as T;
  } finally {
    clearTimeout(timer);
  }
}

interface Ticker24hr {
  symbol: string;
  quoteVolume: string;
}

type KlineRow = unknown[];

export async function topUsdtSymbols(n: number = CRYPTO_TOP_N): Promise<string[]> {
  const data = await get<Ticker24hr[]>(`${SPOT}/api/v3/ticker/24hr`);
  const rows: [string, number][] = [];
  for (const t of data) {
    const sym = t.symbol;
    if (!sym.endsWith("USDT")) continue;
    const base = sym.slice(0, -4);
    if (STABLECOINS.has(base) || LEVERAGED_SUFFIXES.some((s) => base.endsWith(s))) continue;
    const qv = parseFloat(t.quoteVolume ?? "0");
    if (qv < MIN_CRYPTO_QUOTE_VOLUME) continue;
    rows.push([sym, qv]);
  }
  rows.sort((a, b) => b[1] - a[1]);
  return rows.slice(0, n).map(([s]) => s);
}

export async function klines(
  symbol: string,
  interval: string = "1d",
  limit: number = 400
): Promise<OHLCVBar[]> {
  const raw = await get<KlineRow[]>(`${SPOT}/api/v3/klines`, { symbol, interval, limit });
  if (!raw.length) return [];
  return raw.map((row) => ({
    time: Number(row[0]),
    open: parseFloat(String(row[1])),
    high: parseFloat(String(row[2])),
    low: parseFloat(String(row[3])),
    close: parseFloat(String(row[4])),
    volume: parseFloat(String(row[5])),
  }));
}

export async function fundingRate(symbol: string): Promise<number | null> {
  try {
    const data = await get<{ lastFundingRate: string }>(
      `${FUTURES}/fapi/v1/premiumIndex`,
      { symbol }
    );
    return parseFloat(data.lastFundingRate);
  } catch {
    return null;
  }
}
