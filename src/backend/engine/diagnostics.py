"""Diagnostica filtri: spiega perché un asset è o non è in watchlist.

Funzioni pure additive — non modificano soglie né logica di detect_setup_* / classify_candidates.
"""
from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd

from config import (
    MAX_STOP_ATR,
    RS_BOTTOM_PERCENTILE,
    RS_TOP_PERCENTILE,
    RVOL_BREAKOUT,
    RVOL_INTEREST,
    STOCK_MIN_ADR_PCT,
    STOCK_MIN_AVG_VOLUME,
    STOCK_MIN_PRICE,
)
from engine.indicators import adr_pct, bollinger_width, ema, rvol
from engine.screener import natural_direction, resolve_candidate_direction
from engine.setups import _market_params, setup_a_metrics, setup_b_metrics

FilterStatus = Literal["pass", "fail", "skip", "warn"]
FilterResult = dict[str, Any]

CRYPTO_MIXED_SYMBOLS = frozenset({"BTCUSDT", "ETHUSDT"})


def _json_val(v: Any) -> float | str | bool | None:
    if v is None or isinstance(v, str):
        return v
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, (np.integer, int)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return float(v)
    return v


def _fr(
    id_: str,
    label: str,
    status: FilterStatus,
    *,
    value: float | str | None = None,
    threshold: float | str | None = None,
    message: str = "",
) -> FilterResult:
    return {
        "id": id_,
        "label": label,
        "status": status,
        "value": _json_val(value),
        "threshold": _json_val(threshold),
        "message": message,
    }


def diagnose_regime(
    regime: dict,
    direction: str,
    *,
    market: str = "crypto",
    symbol: str | None = None,
) -> list[FilterResult]:
    """Semaforo mercato per la direzione richiesta."""
    mode = regime.get("mode", "mixed")
    long_ok = regime.get("long_allowed", False)
    short_ok = regime.get("short_allowed", False)
    half = regime.get("half_size", False)
    results: list[FilterResult] = []

    if mode == "halt":
        results.append(
            _fr(
                "regime_halt",
                "Regime mercato",
                "fail",
                value=mode,
                message="VIX > soglia — nessuna nuova posizione consentita",
            )
        )
        return results

    if direction == "long":
        st: FilterStatus = "pass" if long_ok else "fail"
        msg = "Long consentiti dal regime" if long_ok else f"Regime '{mode}' — long non consentiti"
        results.append(_fr("regime_long", "Long consentiti", st, value=mode, message=msg))
    else:
        st = "pass" if short_ok else "fail"
        msg = "Short consentiti dal regime" if short_ok else f"Regime '{mode}' — short non consentiti"
        results.append(_fr("regime_short", "Short consentiti", st, value=mode, message=msg))

    if half:
        results.append(
            _fr(
                "regime_half_size",
                "Regime misto",
                "warn",
                value="mixed",
                message="Size dimezzata — BTC tra EMA50 e EMA200 (crypto) o SPY/QQQ misti",
            )
        )

    if market == "crypto" and mode == "mixed" and symbol:
        if symbol in CRYPTO_MIXED_SYMBOLS:
            results.append(
                _fr(
                    "crypto_mixed_symbol",
                    "Asset in regime misto",
                    "pass",
                    value=symbol,
                    message="BTC/ETH consentiti in regime misto",
                )
            )
        else:
            results.append(
                _fr(
                    "crypto_mixed_symbol",
                    "Asset in regime misto",
                    "warn",
                    value=symbol,
                    message=f"{symbol} escluso in regime misto — solo BTCUSDT e ETHUSDT",
                )
            )

    return results


def diagnose_screener(
    df: pd.DataFrame,
    rs_score: float | None,
    direction: str,
    long_allowed: bool,
    short_allowed: bool,
    *,
    market: str = "crypto",
) -> list[FilterResult]:
    """Filtri §3: RS percentile, trend EMA50, RVOL informativo; liquidità per stocks."""
    results: list[FilterResult] = []

    if len(df) < 220:
        results.append(
            _fr(
                "history",
                "Storico minimo",
                "fail",
                value=len(df),
                threshold=220,
                message=f"Solo {len(df)} barre — servono almeno 220",
            )
        )
        return results

    close = df["close"]
    last = float(close.iloc[-1])
    e50 = float(ema(close, 50).iloc[-1])

    if market == "stocks":
        avg_vol = float(df["volume"].rolling(20).mean().iloc[-1])
        adr = adr_pct(df)
        price_ok = last >= STOCK_MIN_PRICE
        vol_ok = avg_vol >= STOCK_MIN_AVG_VOLUME
        adr_ok = adr >= STOCK_MIN_ADR_PCT
        results.append(
            _fr(
                "stock_price",
                "Prezzo minimo",
                "pass" if price_ok else "fail",
                value=round(last, 2),
                threshold=STOCK_MIN_PRICE,
                message=f"Prezzo {last:.2f}$ — min {STOCK_MIN_PRICE}$",
            )
        )
        results.append(
            _fr(
                "stock_volume",
                "Volume medio 20g",
                "pass" if vol_ok else "fail",
                value=round(avg_vol),
                threshold=STOCK_MIN_AVG_VOLUME,
                message=f"Vol medio {avg_vol:,.0f} — min {STOCK_MIN_AVG_VOLUME:,.0f}",
            )
        )
        results.append(
            _fr(
                "stock_adr",
                "ADR% (movimento)",
                "pass" if adr_ok else "fail",
                value=round(adr, 2),
                threshold=STOCK_MIN_ADR_PCT,
                message=f"ADR {adr:.2f}% — min {STOCK_MIN_ADR_PCT}%",
            )
        )
        if not (price_ok and vol_ok and adr_ok):
            return results

    if rs_score is None:
        results.append(
            _fr("rs_score", "Forza relativa (RS)", "skip", message="RS non calcolabile")
        )
    else:
        # FASE 2: RS ordina l'attenzione, non esclude. Fuori banda → warn informativo
        # (come rvol_info), mai fail/blocker.
        pct = round(rs_score * 100, 1)
        if direction == "long":
            in_band = rs_score >= RS_TOP_PERCENTILE
            results.append(
                _fr(
                    "rs_long",
                    "RS percentile (ranking)",
                    "pass" if in_band else "warn",
                    value=pct,
                    threshold=RS_TOP_PERCENTILE * 100,
                    message=(
                        f"RS {pct}% — top {int((1 - RS_TOP_PERCENTILE) * 100)}% "
                        if in_band
                        else f"RS {pct}% — sotto top {int((1 - RS_TOP_PERCENTILE) * 100)}%; "
                        f"non esclude (ordina attenzione)"
                    ),
                )
            )
        else:
            in_band = rs_score <= RS_BOTTOM_PERCENTILE
            results.append(
                _fr(
                    "rs_short",
                    "RS percentile (ranking)",
                    "pass" if in_band else "warn",
                    value=pct,
                    threshold=RS_BOTTOM_PERCENTILE * 100,
                    message=(
                        f"RS {pct}% — bottom {int(RS_BOTTOM_PERCENTILE * 100)}% "
                        if in_band
                        else f"RS {pct}% — sopra bottom {int(RS_BOTTOM_PERCENTILE * 100)}%; "
                        f"non esclude (ordina attenzione)"
                    ),
                )
            )

    above_e50 = last > e50
    if direction == "long":
        trend_ok = above_e50
        results.append(
            _fr(
                "trend_ema50",
                "Prezzo sopra EMA50",
                "pass" if trend_ok else "fail",
                value=round(last, 4),
                threshold=round(e50, 4),
                message=f"Prezzo {last:.4g} vs EMA50 {e50:.4g}",
            )
        )
    else:
        trend_ok = last < e50
        results.append(
            _fr(
                "trend_ema50",
                "Prezzo sotto EMA50",
                "pass" if trend_ok else "fail",
                value=round(last, 4),
                threshold=round(e50, 4),
                message=f"Prezzo {last:.4g} vs EMA50 {e50:.4g}",
            )
        )

    rv_series = rvol(df["volume"])
    rv = float(rv_series.iloc[-1]) if pd.notna(rv_series.iloc[-1]) else 0.0
    rv_st: FilterStatus = "warn" if rv >= RVOL_INTEREST else "pass"
    results.append(
        _fr(
            "rvol_info",
            "RVOL (informativo)",
            rv_st,
            value=round(rv, 2),
            threshold=RVOL_INTEREST,
            message=f"RVOL {rv:.2f} — interesse istituzionale da ≥{RVOL_INTEREST} (non blocca candidatura)",
        )
    )

    cand = resolve_candidate_direction(
        rs_score if rs_score is not None else 0.0,
        last,
        e50,
        long_allowed,
        short_allowed,
    )
    overall = cand == direction
    results.append(
        _fr(
            "screener_overall",
            "Candidatura screener",
            "pass" if overall else "fail",
            message="Passa classify_candidates" if overall else "Non passa classify_candidates",
        )
    )

    return results


def diagnose_setup_a(df: pd.DataFrame, direction: str, market: str | None = None) -> dict:
    """Decompone Setup A in check separati — eligible ⟺ detect_setup_a non None."""
    m = setup_a_metrics(df, direction, market)
    if m is None:
        filters = [
            _fr(
                "setup_a_history",
                "Storico minimo",
                "fail",
                value=len(df),
                threshold=220,
                message=f"Solo {len(df)} barre — servono almeno 220 per Setup A",
            )
        ]
        return {"eligible": False, "filters": filters}

    p = _market_params(market)
    rsi_thresh = p["RSI_LONG_MIN"] if direction == "long" else p["RSI_SHORT_MAX"]
    rsi_cmp = ">" if direction == "long" else "<"
    filters = [
        _fr(
            "setup_a_aligned",
            "Trend allineato (EMA20/50/200)",
            "pass" if m["aligned"] else "fail",
            message="EMA20 > EMA50 > EMA200 inclinate" if direction == "long"
            else "EMA20 < EMA50 < EMA200 inclinate",
        ),
        _fr(
            "setup_a_in_zone",
            "Zona pullback EMA20–EMA50",
            "pass" if m["in_zone"] else "fail",
            message="Prezzo nella fascia di valore con buffer ATR",
        ),
        _fr(
            "setup_a_momentum",
            f"RSI {rsi_cmp} {rsi_thresh}",
            "pass" if m["momentum_ok"] else "fail",
            value=round(m["rsi"], 1),
            threshold=rsi_thresh,
            message=f"RSI {m['rsi']:.1f}",
        ),
        _fr(
            "setup_a_volume",
            "Volume in calo (5g < 20g)",
            "pass" if m["vol_declining"] else "fail",
            value=round(m["vol5"]),
            threshold=round(m["vol20"]),
            message=f"Media vol 5g {m['vol5']:,.0f} vs 20g {m['vol20']:,.0f}",
        ),
        _fr(
            "setup_a_stop_geometry",
            "Geometria stop ≤ 2.5×ATR",
            "pass" if m["stop_geometry_ok"] else "fail",
            value=round(m["stop_dist"], 4),
            threshold=round(MAX_STOP_ATR * m["atr"], 4),
            message=f"Distanza trigger-stop {m['stop_dist']:.4g} — max {MAX_STOP_ATR * m['atr']:.4g}",
        ),
    ]
    core_ok = m["aligned"] and m["in_zone"] and m["momentum_ok"] and m["vol_declining"]
    eligible = bool(core_ok and m["stop_geometry_ok"])
    filters.append(
        _fr(
            "setup_a_overall",
            "Setup A complessivo",
            "pass" if eligible else "fail",
            message="Setup A valido" if eligible else "Setup A non valido",
        )
    )
    return {"eligible": eligible, "filters": filters}


def diagnose_setup_b(df: pd.DataFrame, direction: str, market: str | None = None) -> dict:
    """Decompone Setup B — eligible ⟺ detect_setup_b non None (trigger è informativo)."""
    m = setup_b_metrics(df, direction, market)
    if m is None:
        filters = [
            _fr(
                "setup_b_history",
                "Storico minimo",
                "fail",
                value=len(df),
                threshold=220,
                message=f"Solo {len(df)} barre — servono almeno 220 per Setup B",
            )
        ]
        return {"eligible": False, "filters": filters}

    close = df["close"]
    bbw = bollinger_width(close)
    rank_pct = float(bbw.iloc[-60:].rank(pct=True).iloc[-1] * 100) if len(bbw) >= 60 else None

    squeeze_msg = (
        f"Squeeze attivo — BB width {m['bbw_last']:.4f} ≤ soglia {m['bbw_thresh']:.4f}"
        if m["squeeze"]
        else (
            f"Squeeze assente — BB width al {rank_pct:.0f}° percentile"
            f" (serve ≤10°), valore {m['bbw_last']:.4f}"
            if rank_pct is not None
            else f"Squeeze assente — BB width {m['bbw_last']:.4f}"
        )
    )

    ctx_label = "Prezzo sopra EMA200" if direction == "long" else "Prezzo sotto EMA200"
    filters = [
        _fr(
            "setup_b_squeeze",
            "Compressione (squeeze BB)",
            "pass" if m["squeeze"] else "fail",
            value=round(m["bbw_last"], 6),
            threshold=round(m["bbw_thresh"], 6),
            message=squeeze_msg,
        ),
        _fr(
            "setup_b_context_ema200",
            ctx_label,
            "pass" if m["context_ok"] else "fail",
            value=round(m["last"], 4),
            threshold=round(m["e200"], 4),
            message=f"Prezzo {m['last']:.4g} vs EMA200 {m['e200']:.4g}",
        ),
        _fr(
            "setup_b_stop_geometry",
            "Geometria stop ≤ 2.5×ATR",
            "pass" if m["stop_geometry_ok"] else "fail",
            value=round(m["stop_dist"], 4),
            threshold=round(MAX_STOP_ATR * m["atr"], 4),
            message=f"Distanza trigger-stop {m['stop_dist']:.4g}",
        ),
        _fr(
            "setup_b_breakout",
            "Breakout con RVOL (stato)",
            "warn" if m["breakout_triggered"] else "pass",
            value=round(m["rvol"], 2),
            threshold=RVOL_BREAKOUT,
            message=(
                f"Trigger attivo — RVOL {m['rvol']:.2f} ≥ {RVOL_BREAKOUT}"
                if m["breakout_triggered"]
                else f"In attesa — RVOL {m['rvol']:.2f}, serve ≥{RVOL_BREAKOUT} oltre il livello"
            ),
        ),
    ]
    eligible = bool(m["squeeze"] and m["context_ok"] and m["stop_geometry_ok"])
    filters.append(
        _fr(
            "setup_b_overall",
            "Setup B complessivo",
            "pass" if eligible else "fail",
            message="Setup B valido" if eligible else "Setup B non valido",
        )
    )
    return {"eligible": eligible, "filters": filters}


def _collect_blockers(
    regime_filters: list[FilterResult],
    screener_filters: list[FilterResult],
    setup_a: dict,
    setup_b: dict,
    *,
    mixed_symbol_warn: bool,
    watchlist_cap: bool,
) -> list[str]:
    """Max 3 blocker principali in italiano."""
    blockers: list[str] = []

    def add_from(filters: list[FilterResult], ids: set[str] | None = None) -> None:
        for f in filters:
            if len(blockers) >= 3:
                return
            if f["status"] not in ("fail", "warn"):
                continue
            if ids and f["id"] not in ids:
                continue
            if f.get("message") and f["message"] not in blockers:
                blockers.append(f["message"])

    add_from(regime_filters, {"regime_halt", "regime_long", "regime_short"})
    if mixed_symbol_warn and len(blockers) < 3:
        blockers.append("Regime misto crypto — solo BTC/ETH ammessi come candidati")
    # rs_long / rs_short: informativi (ranking), non blocker.
    add_from(
        screener_filters,
        {"trend_ema50", "screener_overall", "stock_price", "stock_volume", "stock_adr"},
    )
    if not setup_a["eligible"] and not setup_b["eligible"]:
        for f in setup_a["filters"]:
            if len(blockers) >= 3:
                break
            if f["status"] == "fail" and f["id"] != "setup_a_overall" and f["message"] not in blockers:
                blockers.append(f["message"])
                break
        for f in setup_b["filters"]:
            if len(blockers) >= 3:
                break
            if f["status"] == "fail" and f["id"] != "setup_b_overall" and f["message"] not in blockers:
                blockers.append(f["message"])
                break
    if watchlist_cap and len(blockers) < 3:
        blockers.append("Setup valido ma fuori dalla top 10 watchlist")

    return blockers[:3]


def diagnose_asset(
    market: str,
    symbol: str,
    df: pd.DataFrame,
    regime: dict,
    rs_score: float | None,
    *,
    long_allowed: bool | None = None,
    short_allowed: bool | None = None,
    on_watchlist: bool = False,
    watchlist_eligible: bool | None = None,
    mixed_filtered: bool = False,
    capped_out: bool = False,
) -> dict:
    """Diagnostica completa per un singolo asset."""
    long_allowed = regime["long_allowed"] if long_allowed is None else long_allowed
    short_allowed = regime["short_allowed"] if short_allowed is None else short_allowed

    last = float(df["close"].iloc[-1]) if len(df) else 0.0
    e50 = float(ema(df["close"], 50).iloc[-1]) if len(df) >= 50 else 0.0

    suggested = natural_direction(rs_score, last, e50) if rs_score is not None and len(df) >= 220 else None

    cand_dir = (
        resolve_candidate_direction(rs_score or 0, last, e50, long_allowed, short_allowed)
        if rs_score is not None and len(df) >= 220
        else None
    )

    if watchlist_eligible is None:
        # FASE 2: eleggibilità = trend EMA50. Regime/mixed/halt non escludono.
        eligible = cand_dir is not None
        if market == "crypto" and regime.get("mode") == "mixed" and symbol not in CRYPTO_MIXED_SYMBOLS:
            mixed_filtered = True  # solo warning informativo
        watchlist_eligible = eligible

    direction = cand_dir or suggested or "long"
    if watchlist_eligible and cand_dir:
        direction = cand_dir

    setup_a = diagnose_setup_a(df, direction, market)
    setup_b = diagnose_setup_b(df, direction, market)

    best_setup: str | None = None
    if setup_a["eligible"]:
        best_setup = "A"
    elif setup_b["eligible"]:
        best_setup = "B"

    regime_filters = diagnose_regime(regime, direction, market=market, symbol=symbol)
    screener_filters = diagnose_screener(
        df, rs_score, direction, long_allowed, short_allowed, market=market
    )

    mixed_warn = mixed_filtered or (
        market == "crypto"
        and regime.get("mode") == "mixed"
        and symbol not in CRYPTO_MIXED_SYMBOLS
        and not on_watchlist
    )

    blockers = _collect_blockers(
        regime_filters,
        screener_filters,
        setup_a,
        setup_b,
        mixed_symbol_warn=mixed_warn and not watchlist_eligible,
        watchlist_cap=capped_out,
    )

    return {
        "market": market,
        "symbol": symbol,
        "last_price": last,
        "rs_score": round(rs_score, 3) if rs_score is not None else None,
        "direction": direction,
        "suggested_direction": suggested,
        "watchlist_eligible": bool(watchlist_eligible),
        "regime_filters": regime_filters,
        "screener_filters": screener_filters,
        "setup_a": {"eligible": bool(setup_a["eligible"]), "filters": setup_a["filters"]},
        "setup_b": {"eligible": bool(setup_b["eligible"]), "filters": setup_b["filters"]},
        "best_setup": best_setup,
        "on_watchlist": bool(on_watchlist),
        "blockers": blockers,
    }
