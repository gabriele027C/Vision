/** Diagnostica filtri: spiega perché un asset è o non è in watchlist.
 *
 * Funzioni pure additive — non modificano soglie né logica di detect_setup_* / classify_candidates.
 */
import {
  MAX_STOP_ATR,
  RS_BOTTOM_PERCENTILE,
  RS_TOP_PERCENTILE,
  RVOL_BREAKOUT,
  RVOL_INTEREST,
  STOCK_MIN_ADR_PCT,
  STOCK_MIN_AVG_VOLUME,
  STOCK_MIN_PRICE,
} from "../config";
import { adrPct, bollingerWidth, ema, rvol } from "./indicators";
import { naturalDirection, resolveCandidateDirection } from "./screener";
import { setupAMetrics, setupBMetrics } from "./setups";
import type { AssetDiagnostics, FilterResult, FilterStatus, OHLCVBar } from "./types";

const CRYPTO_MIXED_SYMBOLS = new Set(["BTCUSDT", "ETHUSDT"]);

function jsonVal(v: unknown): number | string | null {
  if (v == null) return null;
  if (typeof v === "string") return v;
  if (typeof v === "number") return Number.isFinite(v) ? v : null;
  if (typeof v === "boolean") return v ? 1 : 0;
  return null;
}

function fr(
  id: string,
  label: string,
  status: FilterStatus,
  opts: {
    value?: number | string | null;
    threshold?: number | string | null;
    message?: string;
  } = {}
): FilterResult {
  return {
    id,
    label,
    status,
    value: jsonVal(opts.value ?? null),
    threshold: jsonVal(opts.threshold ?? null),
    message: opts.message ?? "",
  };
}

function rollingMean(arr: number[], window: number): number {
  if (arr.length < window) return NaN;
  const slice = arr.slice(-window);
  return slice.reduce((a, b) => a + b, 0) / window;
}

function rankPctLast(series: number[]): number | null {
  const slice = series.slice(-60);
  if (slice.length < 60) return null;
  const last = slice[slice.length - 1];
  let less = 0;
  let equal = 0;
  for (const v of slice) {
    if (v < last) less++;
    else if (v === last) equal++;
  }
  return ((less + equal * 0.5) / slice.length) * 100;
}

export function diagnoseRegime(
  regime: Record<string, unknown>,
  direction: string,
  opts: { market?: string; symbol?: string | null } = {}
): FilterResult[] {
  const market = opts.market ?? "crypto";
  const symbol = opts.symbol ?? null;
  const mode = (regime.mode as string) ?? "mixed";
  const longOk = Boolean(regime.long_allowed);
  const shortOk = Boolean(regime.short_allowed);
  const half = Boolean(regime.half_size);
  const results: FilterResult[] = [];

  if (mode === "halt") {
    results.push(
      fr("regime_halt", "Regime mercato", "fail", {
        value: mode,
        message: "VIX > soglia — nessuna nuova posizione consentita",
      })
    );
    return results;
  }

  if (direction === "long") {
    const st: FilterStatus = longOk ? "pass" : "fail";
    const msg = longOk ? "Long consentiti dal regime" : `Regime '${mode}' — long non consentiti`;
    results.push(fr("regime_long", "Long consentiti", st, { value: mode, message: msg }));
  } else {
    const st: FilterStatus = shortOk ? "pass" : "fail";
    const msg = shortOk ? "Short consentiti dal regime" : `Regime '${mode}' — short non consentiti`;
    results.push(fr("regime_short", "Short consentiti", st, { value: mode, message: msg }));
  }

  if (half) {
    results.push(
      fr("regime_half_size", "Regime misto", "warn", {
        value: "mixed",
        message: "Size dimezzata — BTC tra EMA50 e EMA200 (crypto) o SPY/QQQ misti",
      })
    );
  }

  if (market === "crypto" && mode === "mixed" && symbol) {
    if (CRYPTO_MIXED_SYMBOLS.has(symbol)) {
      results.push(
        fr("crypto_mixed_symbol", "Asset in regime misto", "pass", {
          value: symbol,
          message: "BTC/ETH consentiti in regime misto",
        })
      );
    } else {
      results.push(
        fr("crypto_mixed_symbol", "Asset in regime misto", "warn", {
          value: symbol,
          message: `${symbol} escluso in regime misto — solo BTCUSDT e ETHUSDT`,
        })
      );
    }
  }

  return results;
}

export function diagnoseScreener(
  bars: OHLCVBar[],
  rsScore: number | null,
  direction: string,
  longAllowed: boolean,
  shortAllowed: boolean,
  opts: { market?: string } = {}
): FilterResult[] {
  const market = opts.market ?? "crypto";
  const results: FilterResult[] = [];

  if (bars.length < 220) {
    results.push(
      fr("history", "Storico minimo", "fail", {
        value: bars.length,
        threshold: 220,
        message: `Solo ${bars.length} barre — servono almeno 220`,
      })
    );
    return results;
  }

  const close = bars.map((b) => b.close);
  const last = close[close.length - 1];
  const e50Series = ema(close, 50);
  const e50 = e50Series[e50Series.length - 1];

  if (market === "stocks") {
    const volume = bars.map((b) => b.volume);
    const avgVol = rollingMean(volume, 20);
    const adr = adrPct(
      bars.map((b) => b.high),
      bars.map((b) => b.low)
    );
    const priceOk = last >= STOCK_MIN_PRICE;
    const volOk = avgVol >= STOCK_MIN_AVG_VOLUME;
    const adrOk = adr >= STOCK_MIN_ADR_PCT;

    results.push(
      fr("stock_price", "Prezzo minimo", priceOk ? "pass" : "fail", {
        value: Math.round(last * 100) / 100,
        threshold: STOCK_MIN_PRICE,
        message: `Prezzo ${last.toFixed(2)}$ — min ${STOCK_MIN_PRICE}$`,
      })
    );
    results.push(
      fr("stock_volume", "Volume medio 20g", volOk ? "pass" : "fail", {
        value: Math.round(avgVol),
        threshold: STOCK_MIN_AVG_VOLUME,
        message: `Vol medio ${avgVol.toLocaleString("en-US", { maximumFractionDigits: 0 })} — min ${STOCK_MIN_AVG_VOLUME.toLocaleString("en-US", { maximumFractionDigits: 0 })}`,
      })
    );
    results.push(
      fr("stock_adr", "ADR% (movimento)", adrOk ? "pass" : "fail", {
        value: Math.round(adr * 100) / 100,
        threshold: STOCK_MIN_ADR_PCT,
        message: `ADR ${adr.toFixed(2)}% — min ${STOCK_MIN_ADR_PCT}%`,
      })
    );
    if (!(priceOk && volOk && adrOk)) return results;
  }

  if (rsScore == null) {
    results.push(fr("rs_score", "Forza relativa (RS)", "skip", { message: "RS non calcolabile" }));
  } else {
    const pct = Math.round(rsScore * 1000) / 10;
    if (direction === "long") {
      const rsOk = rsScore >= RS_TOP_PERCENTILE;
      results.push(
        fr("rs_long", "RS top 20%", rsOk ? "pass" : "fail", {
          value: pct,
          threshold: RS_TOP_PERCENTILE * 100,
          message: `RS ${pct}% — serve ≥${RS_TOP_PERCENTILE * 100}% per long`,
        })
      );
    } else {
      const rsOk = rsScore <= RS_BOTTOM_PERCENTILE;
      results.push(
        fr("rs_short", "RS bottom 20%", rsOk ? "pass" : "fail", {
          value: pct,
          threshold: RS_BOTTOM_PERCENTILE * 100,
          message: `RS ${pct}% — serve ≤${RS_BOTTOM_PERCENTILE * 100}% per short`,
        })
      );
    }
  }

  const aboveE50 = last > e50;
  if (direction === "long") {
    const trendOk = aboveE50;
    results.push(
      fr("trend_ema50", "Prezzo sopra EMA50", trendOk ? "pass" : "fail", {
        value: Math.round(last * 10000) / 10000,
        threshold: Math.round(e50 * 10000) / 10000,
        message: `Prezzo ${last.toPrecision(4)} vs EMA50 ${e50.toPrecision(4)}`,
      })
    );
  } else {
    const trendOk = last < e50;
    results.push(
      fr("trend_ema50", "Prezzo sotto EMA50", trendOk ? "pass" : "fail", {
        value: Math.round(last * 10000) / 10000,
        threshold: Math.round(e50 * 10000) / 10000,
        message: `Prezzo ${last.toPrecision(4)} vs EMA50 ${e50.toPrecision(4)}`,
      })
    );
  }

  const rvSeries = rvol(bars.map((b) => b.volume));
  const rvVal = rvSeries[rvSeries.length - 1];
  const rv = rvVal != null && !Number.isNaN(rvVal) ? rvVal : 0;
  const rvSt: FilterStatus = rv >= RVOL_INTEREST ? "warn" : "pass";
  results.push(
    fr("rvol_info", "RVOL (informativo)", rvSt, {
      value: Math.round(rv * 100) / 100,
      threshold: RVOL_INTEREST,
      message: `RVOL ${rv.toFixed(2)} — interesse istituzionale da ≥${RVOL_INTEREST} (non blocca candidatura)`,
    })
  );

  const cand = resolveCandidateDirection(
    rsScore ?? 0,
    last,
    e50,
    longAllowed,
    shortAllowed
  );
  const overall = cand === direction;
  results.push(
    fr("screener_overall", "Candidatura screener", overall ? "pass" : "fail", {
      message: overall ? "Passa classify_candidates" : "Non passa classify_candidates",
    })
  );

  return results;
}

export function diagnoseSetupA(
  bars: OHLCVBar[],
  direction: string
): { eligible: boolean; filters: FilterResult[] } {
  const m = setupAMetrics(bars, direction);
  if (m == null) {
    return {
      eligible: false,
      filters: [
        fr("setup_a_history", "Storico minimo", "fail", {
          value: bars.length,
          threshold: 220,
          message: `Solo ${bars.length} barre — servono almeno 220 per Setup A`,
        }),
      ],
    };
  }

  const rsiThresh = direction === "long" ? 40 : 60;
  const rsiCmp = direction === "long" ? ">" : "<";
  const filters: FilterResult[] = [
    fr("setup_a_aligned", "Trend allineato (EMA20/50/200)", m.aligned ? "pass" : "fail", {
      message:
        direction === "long"
          ? "EMA20 > EMA50 > EMA200 inclinate"
          : "EMA20 < EMA50 < EMA200 inclinate",
    }),
    fr("setup_a_in_zone", "Zona pullback EMA20–EMA50", m.in_zone ? "pass" : "fail", {
      message: "Prezzo nella fascia di valore con buffer ATR",
    }),
    fr("setup_a_momentum", `RSI ${rsiCmp} ${rsiThresh}`, m.momentum_ok ? "pass" : "fail", {
      value: Math.round(m.rsi * 10) / 10,
      threshold: rsiThresh,
      message: `RSI ${m.rsi.toFixed(1)}`,
    }),
    fr("setup_a_volume", "Volume in calo (5g < 20g)", m.vol_declining ? "pass" : "fail", {
      value: Math.round(m.vol5),
      threshold: Math.round(m.vol20),
      message: `Media vol 5g ${m.vol5.toLocaleString("en-US", { maximumFractionDigits: 0 })} vs 20g ${m.vol20.toLocaleString("en-US", { maximumFractionDigits: 0 })}`,
    }),
    fr("setup_a_stop_geometry", "Geometria stop ≤ 2.5×ATR", m.stop_geometry_ok ? "pass" : "fail", {
      value: Math.round(m.stop_dist * 10000) / 10000,
      threshold: Math.round(MAX_STOP_ATR * m.atr * 10000) / 10000,
      message: `Distanza trigger-stop ${m.stop_dist.toPrecision(4)} — max ${(MAX_STOP_ATR * m.atr).toPrecision(4)}`,
    }),
  ];

  const coreOk = m.aligned && m.in_zone && m.momentum_ok && m.vol_declining;
  const eligible = Boolean(coreOk && m.stop_geometry_ok);
  filters.push(
    fr("setup_a_overall", "Setup A complessivo", eligible ? "pass" : "fail", {
      message: eligible ? "Setup A valido" : "Setup A non valido",
    })
  );
  return { eligible, filters };
}

export function diagnoseSetupB(
  bars: OHLCVBar[],
  direction: string
): { eligible: boolean; filters: FilterResult[] } {
  const m = setupBMetrics(bars, direction);
  if (m == null) {
    return {
      eligible: false,
      filters: [
        fr("setup_b_history", "Storico minimo", "fail", {
          value: bars.length,
          threshold: 220,
          message: `Solo ${bars.length} barre — servono almeno 220 per Setup B`,
        }),
      ],
    };
  }

  const close = bars.map((b) => b.close);
  const bbw = bollingerWidth(close);
  const rankPct = rankPctLast(bbw);

  const squeezeMsg = m.squeeze
    ? `Squeeze attivo — BB width ${m.bbw_last.toFixed(4)} ≤ soglia ${m.bbw_thresh.toFixed(4)}`
    : rankPct != null
      ? `Squeeze assente — BB width al ${Math.round(rankPct)}° percentile (serve ≤10°), valore ${m.bbw_last.toFixed(4)}`
      : `Squeeze assente — BB width ${m.bbw_last.toFixed(4)}`;

  const ctxLabel = direction === "long" ? "Prezzo sopra EMA200" : "Prezzo sotto EMA200";
  const filters: FilterResult[] = [
    fr("setup_b_squeeze", "Compressione (squeeze BB)", m.squeeze ? "pass" : "fail", {
      value: Math.round(m.bbw_last * 1e6) / 1e6,
      threshold: Math.round(m.bbw_thresh * 1e6) / 1e6,
      message: squeezeMsg,
    }),
    fr("setup_b_context_ema200", ctxLabel, m.context_ok ? "pass" : "fail", {
      value: Math.round(m.last * 10000) / 10000,
      threshold: Math.round(m.e200 * 10000) / 10000,
      message: `Prezzo ${m.last.toPrecision(4)} vs EMA200 ${m.e200.toPrecision(4)}`,
    }),
    fr("setup_b_stop_geometry", "Geometria stop ≤ 2.5×ATR", m.stop_geometry_ok ? "pass" : "fail", {
      value: Math.round(m.stop_dist * 10000) / 10000,
      threshold: Math.round(MAX_STOP_ATR * m.atr * 10000) / 10000,
      message: `Distanza trigger-stop ${m.stop_dist.toPrecision(4)}`,
    }),
    fr("setup_b_breakout", "Breakout con RVOL (stato)", m.breakout_triggered ? "warn" : "pass", {
      value: Math.round(m.rvol * 100) / 100,
      threshold: RVOL_BREAKOUT,
      message: m.breakout_triggered
        ? `Trigger attivo — RVOL ${m.rvol.toFixed(2)} ≥ ${RVOL_BREAKOUT}`
        : `In attesa — RVOL ${m.rvol.toFixed(2)}, serve ≥${RVOL_BREAKOUT} oltre il livello`,
    }),
  ];

  const eligible = Boolean(m.squeeze && m.context_ok && m.stop_geometry_ok);
  filters.push(
    fr("setup_b_overall", "Setup B complessivo", eligible ? "pass" : "fail", {
      message: eligible ? "Setup B valido" : "Setup B non valido",
    })
  );
  return { eligible, filters };
}

function collectBlockers(
  regimeFilters: FilterResult[],
  screenerFilters: FilterResult[],
  setupA: { eligible: boolean; filters: FilterResult[] },
  setupB: { eligible: boolean; filters: FilterResult[] },
  opts: { mixedSymbolWarn: boolean; watchlistCap: boolean }
): string[] {
  const blockers: string[] = [];

  function addFrom(filters: FilterResult[], ids?: Set<string>) {
    for (const f of filters) {
      if (blockers.length >= 3) return;
      if (f.status !== "fail" && f.status !== "warn") continue;
      if (ids && !ids.has(f.id)) continue;
      if (f.message && !blockers.includes(f.message)) blockers.push(f.message);
    }
  }

  addFrom(regimeFilters, new Set(["regime_halt", "regime_long", "regime_short"]));
  if (opts.mixedSymbolWarn && blockers.length < 3) {
    blockers.push("Regime misto crypto — solo BTC/ETH ammessi come candidati");
  }
  addFrom(
    screenerFilters,
    new Set([
      "rs_long",
      "rs_short",
      "trend_ema50",
      "screener_overall",
      "stock_price",
      "stock_volume",
      "stock_adr",
    ])
  );

  if (!setupA.eligible && !setupB.eligible) {
    for (const f of setupA.filters) {
      if (blockers.length >= 3) break;
      if (f.status === "fail" && f.id !== "setup_a_overall" && !blockers.includes(f.message)) {
        blockers.push(f.message);
        break;
      }
    }
    for (const f of setupB.filters) {
      if (blockers.length >= 3) break;
      if (f.status === "fail" && f.id !== "setup_b_overall" && !blockers.includes(f.message)) {
        blockers.push(f.message);
        break;
      }
    }
  }

  if (opts.watchlistCap && blockers.length < 3) {
    blockers.push("Setup valido ma fuori dalla top 10 watchlist");
  }

  return blockers.slice(0, 3);
}

export function diagnoseAsset(
  market: "crypto" | "stocks",
  symbol: string,
  bars: OHLCVBar[],
  regime: Record<string, unknown>,
  rsScore: number | null,
  opts: {
    longAllowed?: boolean | null;
    shortAllowed?: boolean | null;
    onWatchlist?: boolean;
    watchlistEligible?: boolean | null;
    mixedFiltered?: boolean;
    cappedOut?: boolean;
  } = {}
): AssetDiagnostics {
  let longAllowed =
    opts.longAllowed != null ? opts.longAllowed : Boolean(regime.long_allowed);
  let shortAllowed =
    opts.shortAllowed != null ? opts.shortAllowed : Boolean(regime.short_allowed);
  let mixedFiltered = opts.mixedFiltered ?? false;

  const last = bars.length ? bars[bars.length - 1].close : 0;
  const close = bars.map((b) => b.close);
  const e50Series = ema(close, 50);
  const e50 = bars.length >= 50 ? e50Series[e50Series.length - 1] : 0;

  const suggested =
    rsScore != null && bars.length >= 220
      ? naturalDirection(rsScore, last, e50)
      : null;

  const candDir =
    rsScore != null && bars.length >= 220
      ? resolveCandidateDirection(rsScore, last, e50, longAllowed, shortAllowed)
      : null;

  let watchlistEligible = opts.watchlistEligible;
  if (watchlistEligible == null) {
    let eligible = candDir != null;
    if (market === "crypto" && regime.mode === "mixed" && !CRYPTO_MIXED_SYMBOLS.has(symbol)) {
      eligible = false;
      mixedFiltered = true;
    }
    if (market === "stocks" && regime.mode === "halt") {
      eligible = false;
    }
    watchlistEligible = eligible;
  }

  let direction: "long" | "short" = candDir ?? suggested ?? "long";
  if (watchlistEligible && candDir) direction = candDir;

  const setupA = diagnoseSetupA(bars, direction);
  const setupB = diagnoseSetupB(bars, direction);

  let bestSetup: "A" | "B" | null = null;
  if (setupA.eligible) bestSetup = "A";
  else if (setupB.eligible) bestSetup = "B";

  const regimeFilters = diagnoseRegime(regime, direction, { market, symbol });
  const screenerFilters = diagnoseScreener(
    bars,
    rsScore,
    direction,
    longAllowed,
    shortAllowed,
    { market }
  );

  const mixedWarn =
    mixedFiltered ||
    (market === "crypto" &&
      regime.mode === "mixed" &&
      !CRYPTO_MIXED_SYMBOLS.has(symbol) &&
      !opts.onWatchlist);

  const blockers = collectBlockers(regimeFilters, screenerFilters, setupA, setupB, {
    mixedSymbolWarn: mixedWarn && !watchlistEligible,
    watchlistCap: opts.cappedOut ?? false,
  });

  return {
    market,
    symbol,
    last_price: last,
    rs_score: rsScore != null ? Math.round(rsScore * 1000) / 1000 : null,
    direction,
    suggested_direction: suggested,
    watchlist_eligible: Boolean(watchlistEligible),
    regime_filters: regimeFilters,
    screener_filters: screenerFilters,
    setup_a: { eligible: setupA.eligible, filters: setupA.filters },
    setup_b: { eligible: setupB.eligible, filters: setupB.filters },
    best_setup: bestSetup,
    on_watchlist: Boolean(opts.onWatchlist),
    blockers,
  };
}
