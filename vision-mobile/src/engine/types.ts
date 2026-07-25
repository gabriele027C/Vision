export interface OHLCVBar {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Regime {
  market: string;
  mode: "long" | "short" | "mixed" | "halt";
  long_allowed: boolean;
  short_allowed: boolean;
  half_size: boolean;
  detail: Record<string, string | number | null>;
}

export interface WatchRow {
  market: "crypto" | "stocks";
  symbol: string;
  direction: "long" | "short";
  rs_score: number;
  rvol: number;
  last_price: number;
  setup: "A" | "B";
  entry_trigger: number;
  stop: number;
  atr: number;
  status: "watch" | "near" | "triggered" | "blocked";
  note: string;
  funding: number | null;
  warnings: string[];
}

export interface Alert {
  id: number;
  created_at: string;
  market: string;
  symbol: string;
  message: string;
  read: number;
}

export interface AppState {
  scanning: boolean;
  progress: string;
  last_scan: string | null;
  last_error: string | null;
  regimes: Record<string, Regime>;
  watchlist: { crypto: WatchRow[]; stocks: WatchRow[] };
  alerts: Alert[];
  unread_alerts: number;
}

export interface Sizing {
  risk_amount: number;
  stop_distance: number;
  stop_distance_pct: number;
  size_units: number;
  notional: number;
  half_size: boolean;
  target_2r_long: number;
  target_2r_short: number;
  direction: "long" | "short";
  market: "crypto" | "stocks";
  leverage: number;
  max_leverage: number;
  leverage_capped: boolean;
  liq_price: number | null;
  liq_safe: boolean;
  round_trip_cost: number;
  target_2r_net_long: number;
  target_2r_net_short: number;
}

export interface SizingError {
  error: string;
}

export type SizingResult = Sizing | SizingError;

export function isSizingError(r: SizingResult): r is SizingError {
  return "error" in r;
}

export interface Trade {
  id: number;
  symbol: string;
  market: string;
  direction: string;
  setup: string;
  entry_price: number;
  stop_price: number;
  size: number;
  risk_amount: number;
  status: "open" | "closed";
  exit_price: number | null;
  r_result: number | null;
  mistake: number;
  notes: string;
  opened_at: string;
  closed_at: string | null;
}

export interface Metrics {
  total_trades: number;
  open_trades: number;
  closed_trades: number;
  validation_target: number;
  validation_progress_pct: number;
  win_rate: number | null;
  expectancy: number | null;
  profit_factor: number | null;
  avg_win_r: number | null;
  avg_loss_r: number | null;
  max_drawdown_r: number | null;
  equity_curve: { trade: number; cum_r: number }[];
  validation_passed: boolean;
  mistakes: number;
}

export interface Settings {
  capital: number;
  risk_pct: number;
  telegram_token: string;
  telegram_chat_id: string;
  scan_interval_min: number;
}

export type FilterStatus = "pass" | "fail" | "skip" | "warn";

export interface FilterResult {
  id: string;
  label: string;
  status: FilterStatus;
  value: number | string | null;
  threshold: number | string | null;
  message: string;
}

export interface SetupDiagnostics {
  eligible: boolean;
  filters: FilterResult[];
}

export interface AssetDiagnostics {
  market: "crypto" | "stocks";
  symbol: string;
  last_price: number;
  rs_score: number | null;
  direction: "long" | "short";
  suggested_direction: "long" | "short" | null;
  watchlist_eligible: boolean;
  regime_filters: FilterResult[];
  screener_filters: FilterResult[];
  setup_a: SetupDiagnostics;
  setup_b: SetupDiagnostics;
  best_setup: "A" | "B" | null;
  on_watchlist: boolean;
  blockers: string[];
}

export interface DiagnosticsResponse {
  market: string;
  items: AssetDiagnostics[];
  symbols: string[];
}

export type RootTabParamList = {
  Dashboard: undefined;
  Watchlist: undefined;
  Diagnostica: undefined;
  Planner: undefined;
  Journal: undefined;
  Impostazioni: undefined;
};
