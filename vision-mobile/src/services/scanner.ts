/** Scanner: orchestra regime → screener → setup → watchlist → alert. */
import {
  FUNDING_BLOCK,
  FUNDING_EXTREME,
  STOCK_MIN_ADR_PCT,
  STOCK_MIN_AVG_VOLUME,
  STOCK_MIN_PRICE,
  WATCHLIST_SIZE,
} from "../config";
import * as binanceClient from "../data/binanceClient";
import * as stocksClient from "../data/stocksClient";
import { diagnoseAsset } from "../engine/diagnostics";
import { adrPct } from "../engine/indicators";
import { cryptoRegime, stockRegime } from "../engine/regime";
import { classifyCandidates, rsScores, type ScreenerCandidate } from "../engine/screener";
import { detectSetupA, detectSetupB, triggerStatus4h } from "../engine/setups";
import type {
  AssetDiagnostics,
  DiagnosticsResponse,
  OHLCVBar,
  Regime,
  WatchRow,
} from "../engine/types";
import { notify } from "./alerts";

const MAX_4H_CHECKS = 15;
const DIAG_TOP_N = 30;
const CRYPTO_MIXED = new Set(["BTCUSDT", "ETHUSDT"]);

export interface ScannerSnapshot {
  scanning: boolean;
  progress: string;
  last_scan: string | null;
  last_error: string | null;
  regimes: Record<string, Regime>;
  watchlist: { crypto: WatchRow[]; stocks: WatchRow[] };
}

interface MarketCtx {
  regime: Regime;
  data: Record<string, OHLCVBar[]>;
  scores: Record<string, number>;
  candidates: ScreenerCandidate[];
  all_with_setup: WatchRow[];
  bench: OHLCVBar[];
}

let scanning = false;
let lastScan: string | null = null;
let lastError: string | null = null;
let progress = "";
let regimes: Record<string, Regime> = {};
let watchlist: { crypto: WatchRow[]; stocks: WatchRow[] } = { crypto: [], stocks: [] };
const diagnostics: { crypto: Record<string, AssetDiagnostics>; stocks: Record<string, AssetDiagnostics> } = {
  crypto: {},
  stocks: {},
};
const marketCtx: Partial<Record<"crypto" | "stocks", MarketCtx>> = {};
const prevTriggered = new Set<string>();

function nowIso(): string {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "+00:00");
}

function dropLast(bars: OHLCVBar[]): OHLCVBar[] {
  return bars.length > 0 ? bars.slice(0, -1) : bars;
}

function rollingMeanLast(arr: number[], window: number): number {
  if (arr.length < window) return NaN;
  const slice = arr.slice(-window);
  return slice.reduce((a, b) => a + b, 0) / window;
}

/** Funding estremo contro la direzione → status "blocked" — speculare a scanner.py. */
export function applyFundingToRow(
  row: WatchRow,
  fr: number | null,
  fundingBlock: boolean | null = null
): void {
  if (fr == null) return;
  const block = fundingBlock ?? FUNDING_BLOCK;
  row.funding = fr;
  const extreme =
    (row.direction === "long" && fr > FUNDING_EXTREME) ||
    (row.direction === "short" && fr < -FUNDING_EXTREME);
  if (!extreme) return;
  if (block) {
    row.status = "blocked";
    row.warnings.push(
      "Funding estremo contro la direzione: trade bloccato, rischio squeeze (§9)"
    );
  } else {
    row.warnings.push("Funding estremo: affollamento, rischio squeeze (§9)");
  }
}

function normalizeSymbol(market: string, symbol: string): string {
  const sym = symbol.toUpperCase().trim();
  if (market === "stocks") return sym.replace(/\./g, "-");
  if (sym.endsWith("USDT")) return sym;
  return `${sym}USDT`;
}

function setProgress(msg: string): void {
  progress = msg;
  console.info(msg);
}

export function snapshot(): ScannerSnapshot {
  return {
    scanning,
    progress,
    last_scan: lastScan,
    last_error: lastError,
    regimes: { ...regimes },
    watchlist: {
      crypto: [...watchlist.crypto],
      stocks: [...watchlist.stocks],
    },
  };
}

export function getDiagnostics(
  market: "crypto" | "stocks",
  symbols?: string[] | null
): DiagnosticsResponse {
  let cache = { ...diagnostics[market] };
  if (symbols?.length) {
    const norm = new Set(symbols.map((s) => normalizeSymbol(market, s)));
    cache = Object.fromEntries(Object.entries(cache).filter(([k]) => norm.has(k)));
  }
  return {
    market,
    items: Object.values(cache),
    symbols: Object.keys(cache),
  };
}

export async function getSymbolDiagnostic(
  market: "crypto" | "stocks",
  symbol: string
): Promise<AssetDiagnostics | null> {
  const sym = normalizeSymbol(market, symbol);
  const hit = diagnostics[market][sym];
  const ctx = marketCtx[market];
  if (hit) return hit;
  if (!ctx) return null;

  let result = diagnoseOne(market, sym, ctx);
  if (!result) result = await fetchAndDiagnose(market, sym, ctx);
  if (result) diagnostics[market][sym] = result;
  return result;
}

export async function runScan(): Promise<void> {
  if (scanning) return;
  scanning = true;
  lastError = null;
  try {
    await scanCrypto();
    await scanStocks();
    lastScan = nowIso();
    progress = "";
  } catch (exc) {
    console.error("scan fallito:", exc);
    lastError = exc instanceof Error ? exc.message : String(exc);
  } finally {
    scanning = false;
  }
}

async function scanCrypto(): Promise<void> {
  setProgress("Crypto: scarico dati Binance...");
  const btcRaw = await binanceClient.klines("BTCUSDT", "1d", 400);
  const btc = dropLast(btcRaw);
  const regime = cryptoRegime(btc);

  const data: Record<string, OHLCVBar[]> = {};
  const symbols = await binanceClient.topUsdtSymbols();
  for (const sym of symbols) {
    const raw = await binanceClient.klines(sym, "1d", 400);
    if (raw.length >= 221) {
      data[sym] = dropLast(raw);
    }
  }

  setProgress("Crypto: screener forza relativa...");
  const scores = rsScores(data, btc);
  let candidates = classifyCandidates(
    data,
    scores,
    regime.long_allowed,
    regime.short_allowed
  );
  if (regime.mode === "mixed") {
    candidates = candidates.filter((c) => CRYPTO_MIXED.has(c.symbol));
  }

  setProgress("Crypto: rilevamento setup...");
  const { rows, allWithSetup } = detectSetups("crypto", candidates, data);

  for (const row of rows.slice(0, MAX_4H_CHECKS)) {
    const df4Raw = await binanceClient.klines(row.symbol, "4h", 200);
    const df4 = dropLast(df4Raw);
    if (df4.length) {
      row.status = triggerStatus4h(df4, row.direction, row.entry_trigger);
    }
    const fr = await binanceClient.fundingRate(row.symbol);
    applyFundingToRow(row, fr);
  }

  const ctx: MarketCtx = {
    regime,
    data,
    scores,
    candidates,
    all_with_setup: allWithSetup,
    bench: btc,
  };
  buildDiagnosticsCache("crypto", ctx, rows);
  finalize("crypto", regime, rows);
}

async function scanStocks(): Promise<void> {
  setProgress("Stocks: scarico universo S&P500 + Nasdaq100...");
  const universe = await stocksClient.stockUniverse();
  const bench = await stocksClient.dailyHistory(["SPY", "QQQ", "^VIX"], "2y", false, 50);
  const spy = bench.SPY;
  const qqq = bench.QQQ;
  const vixDf = bench["^VIX"];
  const vixLast = vixDf?.length ? vixDf[vixDf.length - 1].close : null;

  if (!spy?.length || !qqq?.length) {
    throw new Error("dati SPY/QQQ non disponibili da Yahoo Finance");
  }

  const regime = stockRegime(spy, qqq, vixLast);

  setProgress(`Stocks: scarico storico daily di ${universe.length} titoli (1-2 min)...`);
  const dataAll = await stocksClient.dailyHistory(universe);

  const data: Record<string, OHLCVBar[]> = {};
  for (const [sym, bars] of Object.entries(dataAll)) {
    const last = bars[bars.length - 1].close;
    const avgVol = rollingMeanLast(
      bars.map((b) => b.volume),
      20
    );
    if (last < STOCK_MIN_PRICE || avgVol < STOCK_MIN_AVG_VOLUME) continue;
    if (adrPct(bars.map((b) => b.high), bars.map((b) => b.low)) < STOCK_MIN_ADR_PCT) continue;
    data[sym] = bars;
  }

  setProgress("Stocks: screener forza relativa...");
  const scores = rsScores(data, spy);
  let candidates = classifyCandidates(
    data,
    scores,
    regime.long_allowed,
    regime.short_allowed
  );
  if (regime.mode === "halt") {
    candidates = [];
  }

  setProgress("Stocks: rilevamento setup...");
  const { rows, allWithSetup } = detectSetups("stocks", candidates, data);

  for (const row of rows.slice(0, MAX_4H_CHECKS)) {
    const df4 = await stocksClient.intraday4h(row.symbol);
    if (df4.length) {
      row.status = triggerStatus4h(df4, row.direction, row.entry_trigger);
    }
  }

  const ctx: MarketCtx = {
    regime,
    data,
    scores,
    candidates,
    all_with_setup: allWithSetup,
    bench: spy,
  };
  buildDiagnosticsCache("stocks", ctx, rows);
  finalize("stocks", regime, rows);
}

function detectSetups(
  market: "crypto" | "stocks",
  candidates: ScreenerCandidate[],
  data: Record<string, OHLCVBar[]>
): { rows: WatchRow[]; allWithSetup: WatchRow[] } {
  const rows: WatchRow[] = [];
  const allWithSetup: WatchRow[] = [];

  for (const cand of candidates) {
    const bars = data[cand.symbol];
    const setup =
      detectSetupA(bars, cand.direction) ?? detectSetupB(bars, cand.direction);
    if (!setup) continue;

    const row: WatchRow = {
      market,
      symbol: cand.symbol,
      direction: cand.direction,
      rs_score: cand.rs_score,
      rvol: cand.rvol,
      last_price: cand.last_price,
      setup: setup.setup,
      entry_trigger: setup.entry_trigger,
      stop: setup.stop,
      atr: setup.atr,
      status: setup.status_hint ?? "watch",
      note: setup.note,
      funding: null,
      warnings: [],
    };
    allWithSetup.push(row);
    if (rows.length < WATCHLIST_SIZE) rows.push(row);
  }

  return { rows, allWithSetup };
}

function diagnoseSymbolsForMarket(
  market: "crypto" | "stocks",
  ctx: MarketCtx,
  watchlistRows: WatchRow[]
): Record<string, AssetDiagnostics> {
  const { regime, data, scores, candidates, all_with_setup } = ctx;

  const candMap = new Map(candidates.map((c) => [c.symbol, c]));
  const wlSymbols = new Set(watchlistRows.map((r) => r.symbol));
  const setupSymbols = new Set(all_with_setup.map((r) => r.symbol));
  const cappedSymbols = new Set([...setupSymbols].filter((s) => !wlSymbols.has(s)));

  let symSet: Set<string>;
  if (market === "crypto") {
    symSet = new Set(Object.keys(data));
  } else {
    const ranked = Object.entries(scores).sort(
      (a, b) => Math.abs(b[1] - 0.5) - Math.abs(a[1] - 0.5)
    );
    symSet = new Set([
      ...ranked.slice(0, DIAG_TOP_N).map(([s]) => s),
      ...wlSymbols,
      ...setupSymbols,
    ]);
  }

  let watchlistEligible = new Set(candMap.keys());
  if (market === "crypto" && regime.mode === "mixed") {
    watchlistEligible = new Set([...watchlistEligible].filter((s) => CRYPTO_MIXED.has(s)));
  }

  const out: Record<string, AssetDiagnostics> = {};
  for (const sym of symSet) {
    if (!data[sym]) continue;
    out[sym] = diagnoseAsset(market, sym, data[sym], regime as unknown as Record<string, unknown>, scores[sym] ?? null, {
      onWatchlist: wlSymbols.has(sym),
      watchlistEligible: watchlistEligible.has(sym),
      mixedFiltered:
        market === "crypto" && regime.mode === "mixed" && !CRYPTO_MIXED.has(sym),
      cappedOut: cappedSymbols.has(sym),
    });
  }
  return out;
}

function diagnoseOne(
  market: "crypto" | "stocks",
  symbol: string,
  ctx: MarketCtx
): AssetDiagnostics | null {
  if (!ctx.data[symbol]) return null;
  return buildAssetDiagnostic(market, symbol, ctx, ctx.data);
}

async function fetchAndDiagnose(
  market: "crypto" | "stocks",
  symbol: string,
  ctx: MarketCtx
): Promise<AssetDiagnostics | null> {
  const data = { ...ctx.data };
  let bench = ctx.bench;

  try {
    if (market === "crypto") {
      if (!data[symbol]) {
        const raw = await binanceClient.klines(symbol, "1d", 400);
        if (raw.length < 221) return null;
        data[symbol] = dropLast(raw);
      }
      if (!bench?.length) {
        const raw = await binanceClient.klines("BTCUSDT", "1d", 400);
        bench = dropLast(raw);
      }
    } else {
      if (!data[symbol]) {
        const fetched = await stocksClient.dailyHistory([symbol], "2y", false, 220);
        if (!fetched[symbol] || fetched[symbol].length < 220) return null;
        data[symbol] = fetched[symbol];
      }
      if (!bench?.length) return null;
    }
  } catch (exc) {
    console.warn(`fetch on-demand ${market}/${symbol} fallito:`, exc);
    return null;
  }

  const scores = rsScores(data, bench);
  const updatedCtx: MarketCtx = {
    ...ctx,
    data,
    scores,
    candidates: classifyCandidates(
      data,
      scores,
      ctx.regime.long_allowed,
      ctx.regime.short_allowed
    ),
  };
  return buildAssetDiagnostic(market, symbol, updatedCtx, data);
}

function buildAssetDiagnostic(
  market: "crypto" | "stocks",
  symbol: string,
  ctx: MarketCtx,
  data: Record<string, OHLCVBar[]>
): AssetDiagnostics {
  const { regime, scores, candidates, all_with_setup } = ctx;
  const wlRows = watchlist[market];
  const wlSymbols = new Set(wlRows.map((r) => r.symbol));
  const setupSymbols = new Set(all_with_setup.map((r) => r.symbol));
  const candMap = new Set(candidates.map((c) => c.symbol));

  let watchlistEligible = new Set(candMap);
  if (market === "crypto" && regime.mode === "mixed") {
    watchlistEligible = new Set([...watchlistEligible].filter((s) => CRYPTO_MIXED.has(s)));
  }

  return diagnoseAsset(market, symbol, data[symbol], regime as unknown as Record<string, unknown>, scores[symbol] ?? null, {
    onWatchlist: wlSymbols.has(symbol),
    watchlistEligible: watchlistEligible.has(symbol),
    mixedFiltered:
      market === "crypto" && regime.mode === "mixed" && !CRYPTO_MIXED.has(symbol),
    cappedOut: setupSymbols.has(symbol) && !wlSymbols.has(symbol),
  });
}

function buildDiagnosticsCache(
  market: "crypto" | "stocks",
  ctx: MarketCtx,
  watchlistRows: WatchRow[]
): void {
  diagnostics[market] = diagnoseSymbolsForMarket(market, ctx, watchlistRows);
  marketCtx[market] = ctx;
}

function finalize(market: "crypto" | "stocks", regime: Regime, rows: WatchRow[]): void {
  for (const row of rows) {
    const key = `${market}:${row.symbol}:${row.direction}:${row.setup}`;
    if (row.status === "triggered" && !prevTriggered.has(key)) {
      notify(
        market,
        row.symbol,
        `TRIGGER Setup ${row.setup} ${row.direction.toUpperCase()} — ` +
          `entrata ${row.entry_trigger}, stop ${row.stop}. ` +
          `Verifica su TradingView e usa il Trade Planner.`
      );
    }
    if (row.status === "triggered") prevTriggered.add(key);
  }
  regimes[market] = regime;
  watchlist[market] = rows;
}

/** Singleton compatibile con import esistenti. */
export const scanner = {
  snapshot,
  runScan,
  getDiagnostics,
  getSymbolDiagnostic,
};
