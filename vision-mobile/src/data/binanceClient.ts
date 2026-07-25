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
const MAX_RETRIES = 3;
const BASE_BACKOFF_MS = 1000;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchOnce<T>(url: string): Promise<T> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    const resp = await fetch(url, { signal: ctrl.signal });
    if (!resp.ok) {
      const err = new Error(`HTTP ${resp.status}: ${url}`) as Error & { status?: number };
      err.status = resp.status;
      throw err;
    }
    return (await resp.json()) as T;
  } finally {
    clearTimeout(timer);
  }
}

/** GET con retry a backoff esponenziale (3 tentativi) su 429/5xx e timeout — speculare a binance_client.py. */
async function get<T>(url: string, params?: Record<string, string | number>): Promise<T> {
  const qs = params
    ? "?" + new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)])).toString()
    : "";
  let delay = BASE_BACKOFF_MS;
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      return await fetchOnce<T>(url + qs);
    } catch (exc) {
      const status = (exc as { status?: number }).status;
      const isTimeout = exc instanceof Error && exc.name === "AbortError";
      const retriable = isTimeout || status === 429 || (status != null && status >= 500);
      if (!retriable || attempt === MAX_RETRIES) throw exc;
      console.warn(
        `[binance] ${isTimeout ? "timeout" : `HTTP ${status}`} su ${url} ` +
          `(tentativo ${attempt}/${MAX_RETRIES}), retry tra ${delay}ms`
      );
      await sleep(delay);
      delay *= 2;
    }
  }
  throw new Error("unreachable");
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
  } catch (exc) {
    console.warn(`[binance] funding rate ${symbol} non disponibile:`, exc);
    return null;
  }
}
