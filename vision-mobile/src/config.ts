// Universo crypto
export const CRYPTO_TOP_N = 50;
export const STABLECOINS = new Set([
  "USDC", "FDUSD", "TUSD", "DAI", "USDP", "PYUSD", "EUR", "EURI",
  "USDE", "BUSD", "UST", "USTC", "AEUR", "XUSD", "USD1", "RLUSD",
  "XAUT", "PAXG",
]);
export const LEVERAGED_SUFFIXES = ["UP", "DOWN", "BULL", "BEAR"];
export const MIN_CRYPTO_QUOTE_VOLUME = 25_000_000;

// Stocks
export const STOCK_MIN_PRICE = 10.0;
export const STOCK_MIN_AVG_VOLUME = 1_000_000;
export const STOCK_MIN_ADR_PCT = 2.0;

// Strategia
export const RS_TOP_PERCENTILE = 0.80;
export const RS_BOTTOM_PERCENTILE = 0.20;
export const RVOL_INTEREST = 1.5;
export const RVOL_BREAKOUT = 2.0;
// RVOL nello screener: default = punteggio combinato 0.7*RS + 0.3*RVOL cappato
// (ordina i candidati, non li taglia). true = scarta RVOL < RVOL_INTEREST.
export const RVOL_HARD_FILTER = false;
export const MAX_STOP_ATR = 2.5;
export const WATCHLIST_SIZE = 10;
export const VIX_HALT = 30.0;
export const FUNDING_EXTREME = 0.0005;
// Funding oltre FUNDING_EXTREME contro la direzione: true = status "blocked".
export const FUNDING_BLOCK = true;

// Parametri setup per mercato (Fase 5)
// ATTENZIONE: IPOTESI INIZIALI, non validate — confermarle con il backtester
// Python (engine/backtest.py, --params default vs market) prima di fidarsi.
export interface MarketParams {
  RANGE_BARS: number;
  SQUEEZE_LOOKBACK: number;
  RSI_LONG_MIN: number;
  RSI_SHORT_MAX: number;
}
export const MARKET_PARAMS: Record<"crypto" | "stocks", MarketParams> = {
  crypto: {
    RANGE_BARS: 21,
    SQUEEZE_LOOKBACK: 84,
    RSI_LONG_MIN: 35,
    RSI_SHORT_MAX: 65,
  },
  stocks: {
    RANGE_BARS: 15,
    SQUEEZE_LOOKBACK: 60,
    RSI_LONG_MIN: 40,
    RSI_SHORT_MAX: 60,
  },
};

/** FASE 3 — IPOTESI NON VALIDATE. Invalidazione più ampia sui TF bassi (rumore/costi). */
export interface TfParams {
  RANGE_BARS: number;
  SQUEEZE_LOOKBACK: number;
  INVALIDATION_ATR: number;
  MIN_BARS: number;
  BINANCE_INTERVAL: string;
}
export const TF_PARAMS: Record<"D" | "4H" | "1H" | "15m", TfParams> = {
  D: { RANGE_BARS: 15, SQUEEZE_LOOKBACK: 60, INVALIDATION_ATR: 1.5, MIN_BARS: 220, BINANCE_INTERVAL: "1d" },
  "4H": { RANGE_BARS: 30, SQUEEZE_LOOKBACK: 90, INVALIDATION_ATR: 1.75, MIN_BARS: 120, BINANCE_INTERVAL: "4h" },
  "1H": { RANGE_BARS: 40, SQUEEZE_LOOKBACK: 120, INVALIDATION_ATR: 2.0, MIN_BARS: 160, BINANCE_INTERVAL: "1h" },
  "15m": { RANGE_BARS: 48, SQUEEZE_LOOKBACK: 144, INVALIDATION_ATR: 2.5, MIN_BARS: 200, BINANCE_INTERVAL: "15m" },
};
export const WATCHLIST_ENTRY_TFS = ["D", "4H"] as const;
export const TIMING_TFS = ["1H", "15m"] as const;
export const TIMING_ALERT_COOLDOWN_S = 4 * 3600;

/**
 * FASE 4 / 5-BIS — IPOTESI NON VALIDATE, da calibrare su casi reali.
 * Stati qualitativi ↑/↓/→ per display e matching playbook.
 */
export const PLAYBOOK_THRESHOLDS = {
  oi: {
    up_pct_24h: 0.05,
    down_pct_24h: -0.05,
    collapse_pct_24h: -0.2,
  },
  cvd: {
    slope_bars: 20,
    // Calibrato 2026-07-27 su scan live: |slope| tipica 0.01–0.04; ±0.1 → tutto flat.
    // IPOTESI NON VALIDATE — riaffinare sull'uso reale.
    up: 0.02,
    down: -0.02,
    down_strong: -0.06,
  },
  prezzo: {
    flat_band: 0.005,
    lookback_bars: 6,
  },
  rvol: {
    high: 1.5,
    low: 1.0,
  },
} as const;
export const OI_HIST_CACHE_TTL_S = 3600;
export const OI_HIST_PERIOD = "4h";
export const FUTURES_KLINES_CACHE_TTL_S = 900;

/** FASE 5 — pesi non validati, sola funzione di ordinamento dell'attenzione. */
export const CONFLUENCE_WEIGHTS = {
  tech: 0.15,
  rs: 0.2,
  cvd_long: 0.25,
  oi_expand: 0.2,
  funding_ok: 0.1,
  rvol: 0.1,
} as const;

export const PLAYBOOK_IN_ALERTS = true;

// Default settings utente
export const DEFAULT_SETTINGS = {
  capital: 4000.0,
  risk_pct: 1.0,
  telegram_token: "",
  telegram_chat_id: "",
  scan_interval_min: 30,
};
