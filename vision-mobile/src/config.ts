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

// Default settings utente
export const DEFAULT_SETTINGS = {
  capital: 4000.0,
  risk_pct: 1.0,
  telegram_token: "",
  telegram_chat_id: "",
  scan_interval_min: 30,
};
