/** Dati azionari via Yahoo Finance HTTP (query1.finance.yahoo.com).

Costituenti (fonti gratuite):
- S&P 500: dataset GitHub `datasets/s-and-p-500-companies` (CSV)
- Nasdaq 100: API pubblica api.nasdaq.com
 */
import AsyncStorage from "@react-native-async-storage/async-storage";
import type { OHLCVBar } from "../engine/types";

const UNIVERSE_CACHE_KEY = "universe_stocks";
const UNIVERSE_MAX_AGE_MS = 7 * 24 * 3600 * 1000;

const SP500_CSV =
  "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv";
const NDX_API = "https://api.nasdaq.com/api/quote/list-type/nasdaq100";
const YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart";
const HEADERS: Record<string, string> = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
  Accept: "application/json",
};

const TIMEOUT_MS = 30_000;

async function fetchText(url: string, headers?: Record<string, string>): Promise<string> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    const resp = await fetch(url, { headers: headers ?? HEADERS, signal: ctrl.signal });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${url}`);
    return resp.text();
  } finally {
    clearTimeout(timer);
  }
}

async function fetchJson<T>(url: string, headers?: Record<string, string>): Promise<T> {
  const text = await fetchText(url, headers);
  return JSON.parse(text) as T;
}

function parseCsvRow(line: string): string[] {
  const out: string[] = [];
  let cur = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (c === '"') {
      inQuotes = !inQuotes;
    } else if (c === "," && !inQuotes) {
      out.push(cur);
      cur = "";
    } else {
      cur += c;
    }
  }
  out.push(cur);
  return out;
}

async function fetchSp500(): Promise<string[]> {
  const text = await fetchText(SP500_CSV);
  const lines = text.trim().split(/\r?\n/);
  const header = parseCsvRow(lines[0]);
  const symIdx = header.indexOf("Symbol");
  if (symIdx < 0) throw new Error("CSV S&P500: colonna Symbol mancante");
  return lines
    .slice(1)
    .map((line) => parseCsvRow(line)[symIdx]?.trim())
    .filter((s): s is string => Boolean(s));
}

async function fetchNasdaq100(): Promise<string[]> {
  const data = await fetchJson<{ data: { data: { rows: { symbol?: string }[] } } }>(NDX_API);
  return data.data.data.rows
    .map((r) => r.symbol?.trim())
    .filter((s): s is string => Boolean(s));
}

interface UniverseCache {
  fetched_at: number;
  symbols: string[];
}

export async function stockUniverse(): Promise<string[]> {
  try {
    const raw = await AsyncStorage.getItem(UNIVERSE_CACHE_KEY);
    if (raw) {
      const cached = JSON.parse(raw) as UniverseCache;
      if (Date.now() - cached.fetched_at < UNIVERSE_MAX_AGE_MS) {
        return cached.symbols;
      }
    }
  } catch {
    /* cache corrigida */
  }

  try {
    const [sp500, ndx] = await Promise.all([fetchSp500(), fetchNasdaq100()]);
    const symbols = [...new Set([...sp500, ...ndx].map((s) => s.replace(/\./g, "-")))].sort();
    if (symbols.length < 400) {
      throw new Error(`universo sospetto: solo ${symbols.length} simboli`);
    }
    const payload: UniverseCache = { fetched_at: Date.now(), symbols };
    await AsyncStorage.setItem(UNIVERSE_CACHE_KEY, JSON.stringify(payload));
    return symbols;
  } catch (exc) {
    console.warn("fetch universo azioni fallito:", exc);
    const raw = await AsyncStorage.getItem(UNIVERSE_CACHE_KEY);
    if (raw) return (JSON.parse(raw) as UniverseCache).symbols;
    throw exc;
  }
}

interface YahooChartResult {
  chart: {
    result: {
      timestamp: number[];
      indicators: {
        quote: {
          open: (number | null)[];
          high: (number | null)[];
          low: (number | null)[];
          close: (number | null)[];
          volume: (number | null)[];
        }[];
        adjclose?: { adjclose: (number | null)[] }[];
      };
    }[] | null;
  };
}

function parseYahooChart(data: YahooChartResult): OHLCVBar[] {
  const result = data.chart.result?.[0];
  if (!result?.timestamp?.length) return [];

  const quote = result.indicators.quote[0];
  const adj = result.indicators.adjclose?.[0]?.adjclose;
  const bars: OHLCVBar[] = [];

  for (let i = 0; i < result.timestamp.length; i++) {
    const close = quote.close[i];
    if (close == null || Number.isNaN(close)) continue;

    let open = quote.open[i] ?? close;
    let high = quote.high[i] ?? close;
    let low = quote.low[i] ?? close;
    let adjClose = close;

    if (adj?.[i] != null && close !== 0) {
      const ratio = adj[i]! / close;
      open *= ratio;
      high *= ratio;
      low *= ratio;
      adjClose = adj[i]!;
    }

    bars.push({
      time: result.timestamp[i] * 1000,
      open,
      high,
      low,
      close: adjClose,
      volume: quote.volume[i] ?? 0,
    });
  }
  return bars;
}

async function yahooChart(
  ticker: string,
  interval: string,
  range: string
): Promise<OHLCVBar[]> {
  const url = `${YAHOO_CHART}/${encodeURIComponent(ticker)}?interval=${interval}&range=${range}`;
  const data = await fetchJson<YahooChartResult>(url);
  return parseYahooChart(data);
}

async function mapConcurrent<T, R>(
  items: T[],
  concurrency: number,
  fn: (item: T) => Promise<R>
): Promise<R[]> {
  const out: R[] = new Array(items.length);
  let idx = 0;
  async function worker() {
    while (idx < items.length) {
      const i = idx++;
      out[i] = await fn(items[i]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, worker));
  return out;
}

const NY_TZ = "America/New_York";

/** Ora di New York per un timestamp ms: {y, m, d, minutes da mezzanotte}.
 *  Fallback UTC-5 se Intl/timezone non è disponibile sul runtime. */
function nyParts(ms: number): { y: number; m: number; d: number; minutes: number } {
  try {
    const fmt = new Intl.DateTimeFormat("en-US", {
      timeZone: NY_TZ,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
    const p: Record<string, string> = {};
    for (const part of fmt.formatToParts(new Date(ms))) p[part.type] = part.value;
    return {
      y: +p.year,
      m: +p.month,
      d: +p.day,
      minutes: (+p.hour % 24) * 60 + +p.minute,
    };
  } catch {
    const d = new Date(ms - 5 * 3600 * 1000);
    return {
      y: d.getUTCFullYear(),
      m: d.getUTCMonth() + 1,
      d: d.getUTCDate(),
      minutes: d.getUTCHours() * 60 + d.getUTCMinutes(),
    };
  }
}

const SESSION_OPEN_MIN = 9 * 60 + 30; // 9:30 ET
const SESSION_CLOSE_MIN = 16 * 60; // 16:00 ET

/** Scarta la barra daily di oggi se la sessione USA non è ancora chiusa:
 *  Yahoo include la barra parziale intraday, che contamina RVOL, trigger,
 *  stop e indicatori (repainting). Speculare a _drop_unclosed_daily nel backend. */
function dropUnclosedDaily(bars: OHLCVBar[]): OHLCVBar[] {
  if (!bars.length) return bars;
  const now = nyParts(Date.now());
  const last = nyParts(bars[bars.length - 1].time);
  const sameDay = now.y === last.y && now.m === last.m && now.d === last.d;
  if (sameDay && now.minutes < SESSION_CLOSE_MIN) {
    return bars.slice(0, -1);
  }
  return bars;
}

export async function dailyHistory(
  tickers: string[],
  period: string = "2y",
  _threads: boolean = true,
  minBars: number = 220
): Promise<Record<string, OHLCVBar[]>> {
  const out: Record<string, OHLCVBar[]> = {};
  const chunkSize = 100;
  const concurrency = _threads ? 8 : 2;

  for (let i = 0; i < tickers.length; i += chunkSize) {
    const chunk = tickers.slice(i, i + chunkSize);
    const results = await mapConcurrent(chunk, concurrency, async (tkr) => {
      try {
        const bars = await yahooChart(tkr, "1d", period);
        const valid = dropUnclosedDaily(
          bars.filter((b) => b.close != null && !Number.isNaN(b.close))
        );
        return valid.length >= minBars ? ([tkr, valid] as const) : null;
      } catch {
        return null;
      }
    });
    for (const row of results) {
      if (row) out[row[0]] = row[1];
    }
  }
  return out;
}

/** Candele 1h (max 60 giorni su Yahoo) ricampionate a 4h, per i trigger di entrata.
 *
 * Le barre sono ancorate alle 9:30 ET e limitate alla regular session:
 * il vecchio bucketing a mezzanotte UTC produceva candele 4H inesistenti
 * su qualsiasi chart (mescolavano pezzi di sessioni diverse). Ritorna solo
 * barre chiuse: la 4H in formazione è esclusa, come per il percorso crypto. */
export async function intraday4h(ticker: string): Promise<OHLCVBar[]> {
  const bars = await yahooChart(ticker, "1h", "60d");
  if (!bars.length) return [];

  // Chiave bucket: giorno ET + indice del blocco 4H dalla 9:30
  // (blocco 0 = 9:30-13:30, blocco 1 = 13:30-16:00).
  const buckets = new Map<string, OHLCVBar>();

  for (const bar of bars) {
    const p = nyParts(bar.time);
    if (p.minutes < SESSION_OPEN_MIN || p.minutes >= SESSION_CLOSE_MIN) continue; // solo cash session
    const block = Math.floor((p.minutes - SESSION_OPEN_MIN) / 240);
    const key = `${p.y}-${p.m}-${p.d}-${block}`;
    const existing = buckets.get(key);
    if (!existing) {
      buckets.set(key, { ...bar });
    } else {
      existing.high = Math.max(existing.high, bar.high);
      existing.low = Math.min(existing.low, bar.low);
      existing.close = bar.close;
      existing.volume += bar.volume;
      existing.time = Math.min(existing.time, bar.time);
    }
  }

  const out = [...buckets.values()]
    .filter((b) => b.close != null && !Number.isNaN(b.close))
    .sort((a, b) => a.time - b.time);

  // Scarta l'ultima barra se non è ancora chiusa: chiude al più presto tra
  // inizio+4h e la chiusura di sessione delle 16:00 del suo giorno.
  if (out.length) {
    const last = out[out.length - 1];
    const start = nyParts(last.time);
    const now = nyParts(Date.now());
    const sameDay = now.y === start.y && now.m === start.m && now.d === start.d;
    const barEndMin = Math.min(start.minutes + 240, SESSION_CLOSE_MIN);
    if (sameDay && now.minutes < barEndMin) {
      out.pop();
    }
  }
  return out;
}

/** Prezzo di mercato corrente (Yahoo 1m → fallback daily con barra di oggi).
 *  Speculare a stocks_client.last_prices — non usa dropUnclosedDaily. */
export async function lastPrices(tickers: string[]): Promise<Record<string, number>> {
  if (!tickers.length) return {};
  const out: Record<string, number> = {};

  await mapConcurrent(tickers, 6, async (tkr) => {
    try {
      const bars1m = await yahooChart(tkr, "1m", "1d");
      if (bars1m.length) {
        out[tkr] = bars1m[bars1m.length - 1].close;
        return;
      }
    } catch {
      /* fallback daily */
    }
    try {
      const barsD = await yahooChart(tkr, "1d", "5d");
      if (barsD.length) out[tkr] = barsD[barsD.length - 1].close;
    } catch (exc) {
      console.warn(`[yahoo] last_prices ${tkr} fallito:`, exc);
    }
  });

  return out;
}
