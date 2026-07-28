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
  /** Livello di rottura (user-facing). Alias di entry_trigger. */
  breakout_level?: number;
  /** @deprecated preferire breakout_level in UI */
  entry_trigger: number;
  stop: number;
  atr: number;
  status: "watch" | "near" | "triggered" | "blocked";
  note: string;
  funding: number | null;
  warnings: string[];
  entry_tf?: string;
  tf_4h?: { squeeze?: boolean; entry_trigger?: number; stop?: number; note?: string };
  timing?: { timeframe?: string; aligned_with_daily?: boolean; note?: string }[];
  oi_state?: "up" | "down" | "flat" | "collapse" | null;
  oi_arrow?: string | null;
  oi_delta_24h?: number | null;
  oi_value?: number | null;
  cvd_state?: "up" | "down" | "flat" | "down_strong" | null;
  cvd_arrow?: string | null;
  cvd_slope?: number | null;
  confluence?: number;
  confluence_breakdown?: Record<
    string,
    {
      weight: number;
      raw: number | null;
      contrib: number | null;
      status: "ok" | "n/d";
      weight_norm?: number;
    }
  >;
  confluence_renorm?: boolean;
  scenario_ids?: string[];
  price_live?: boolean;
  price_asof?: string;
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
  bearish_context?: { crypto: WatchRow[]; stocks: WatchRow[] };
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
  taker_fee?: number;
  funding_est?: number;
  days_held_est?: number;
  fee_round_trip?: number;
  funding_cost_est?: number;
  round_trip_cost: number;
  cost_r?: number;
  target_2r_net_long: number;
  target_2r_net_short: number;
  net_2r_after_costs?: number;
}

export interface SizingError {
  error: string;
  liq_price?: number;
  leverage?: number;
  liq_safe?: boolean;
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
  timeframe?: string | null;
  pattern?: string | null;
  oi_at_entry?: number | null;
  cvd_slope_at_entry?: number | null;
  funding_at_entry?: number | null;
  rvol_at_entry?: number | null;
  mae_r?: number | null;
  mfe_r?: number | null;
  note?: string | null;
  scenario_ids?: string[];
}

export interface MetricsBucket {
  key: string;
  n: number;
  win_rate: number | null;
  expectancy: number | null;
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
  reliable_stats_from_n?: number;
  stats_reliable?: boolean;
  by_timeframe?: MetricsBucket[];
  by_pattern?: MetricsBucket[];
  by_context?: {
    rvol: MetricsBucket[];
    funding: MetricsBucket[];
    oi: MetricsBucket[];
  };
  by_scenario?: {
    scenario_id: string;
    n: number;
    win_rate: number;
    expectancy: number;
    note: string | null;
  }[];
  random_benchmark?: {
    expected_wr_pct: number;
    note: string;
    user_wr_pct: number | null;
    delta_wr_pp: number | null;
  };
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
  price_kind?: "live" | "close_d";
  price_live?: boolean;
  price_asof?: string;
  close_d_price?: number;
  close_d_asof?: string;
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
  scenarios?: Array<{
    id: string;
    famiglia: string;
    titolo: string;
    lettura: string;
    monitorare: string[];
    invalidazione: string;
    errore_tipico: string;
    lato_operativo: boolean;
    footer: string;
  }>;
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
