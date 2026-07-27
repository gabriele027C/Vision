export interface Regime {
  market: string;
  mode: "long" | "short" | "mixed" | "halt";
  long_allowed: boolean;
  short_allowed: boolean;
  half_size: boolean;
  detail: Record<string, string | number | null>;
}

export interface TimingInfo {
  timeframe: string;
  entry_trigger: number;
  stop: number;
  note: string;
  aligned_with_daily?: boolean;
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
  /** TF di ingresso in watchlist (D o 4H). 1H/15m sono solo timing. */
  entry_tf?: string;
  tf_4h?: { squeeze: boolean; entry_trigger?: number; stop?: number; note?: string };
  timing?: TimingInfo[];
  /** FASE 4 — sintesi flusso (opzionali fino a popolamento). */
  oi_state?: "up" | "down" | "flat" | "collapse" | null;
  oi_arrow?: string | null;
  oi_delta_24h?: number | null;
  oi_delta_3d?: number | null;
  oi_value?: number | null;
  cvd_state?: "up" | "down" | "flat" | "down_strong" | null;
  cvd_arrow?: string | null;
  cvd_slope?: number | null;
  flow_combo_label?: string | null;
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
  bearish_context?: {
    crypto: {
      symbol: string;
      rs_score: number;
      rvol: number;
      last_price: number;
      setup: string;
      note: string;
    }[];
    stocks: {
      symbol: string;
      rs_score: number;
      rvol: number;
      last_price: number;
      setup: string;
      note: string;
    }[];
  };
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
  direction?: "long" | "short";
  market?: "crypto" | "stocks";
  leverage?: number;
  max_leverage?: number;
  leverage_capped?: boolean;
  liq_price?: number | null;
  liq_safe?: boolean;
  taker_fee?: number;
  funding_est?: number;
  days_held_est?: number;
  fee_round_trip?: number;
  funding_cost_est?: number;
  round_trip_cost?: number;
  cost_r?: number;
  target_2r_net_long?: number;
  target_2r_net_short?: number;
  net_2r_after_costs?: number;
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
  flow?: {
    oi_value: number | null;
    oi_delta_24h: number | null;
    oi_delta_3d: number | null;
    oi_state: string | null;
    oi_arrow: string | null;
    cvd_slope: number | null;
    cvd_state: string | null;
    cvd_arrow: string | null;
    price_state: string | null;
    combo_key: string;
    combo_label: string;
    combo_message: string;
  } | null;
  flow_filters?: FilterResult[];
}

export interface DiagnosticsResponse {
  market: string;
  items: AssetDiagnostics[];
  symbols: string[];
}
