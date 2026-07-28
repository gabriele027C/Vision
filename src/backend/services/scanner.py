"""Scanner: orchestra regime -> screener -> setup -> watchlist -> alert."""

import logging

import threading

import traceback

from datetime import datetime, timezone



from config import (
    FUNDING_BLOCK,
    FUNDING_EXTREME,
    PLAYBOOK_IN_ALERTS,
    STOCK_MIN_ADR_PCT,
    STOCK_MIN_AVG_VOLUME,
    STOCK_MIN_PRICE,
    WATCHLIST_SIZE,
)

from data import binance_client, stocks_client

from engine import regime as regime_mod

from engine import screener

from engine.timeframes import (
    TimingAlertGate,
    attach_timing_to_row,
    closed_klines,
    detect_compression,
)

from engine.indicators import adr_pct

from engine.setups import detect_setup_a, detect_setup_b, trigger_status_4h

from engine.diagnostics import diagnose_asset

from services.alerts import notify

from services.flow_data import enrich_row_with_flow, fetch_flow_snapshot

from engine.confluence import attach_confluence, sort_by_confluence

from engine.playbook import primary_alert_scenario, scenario_ids_for_row

from services.live_prices import (
    PriceRefreshGate,
    apply_live_prices,
    fetch_live_prices,
    stamp_live_prices,
)


log = logging.getLogger(__name__)

MAX_4H_CHECKS = 15
DIAG_TOP_N = 30


def apply_funding_to_row(row: dict, fr: float | None, funding_block: bool | None = None) -> None:
    """Applica il funding al row: veto (status 'blocked') se estremo contro la direzione.

    Con funding_block=False (o FUNDING_BLOCK=False in config) il comportamento
    torna al solo warning testuale."""

    if fr is None:
        return
    if funding_block is None:
        funding_block = FUNDING_BLOCK
    row["funding"] = fr
    extreme = (row["direction"] == "long" and fr > FUNDING_EXTREME) or (
        row["direction"] == "short" and fr < -FUNDING_EXTREME
    )
    if not extreme:
        return
    if funding_block:
        row["status"] = "blocked"
        row["warnings"].append(
            "Funding estremo contro la direzione: trade bloccato, rischio squeeze (§9)"
        )
    else:
        row["warnings"].append("Funding estremo: affollamento, rischio squeeze (§9)")


def _normalize_symbol(market: str, symbol: str) -> str:

    sym = symbol.upper().strip()

    if market == "stocks":

        return sym.replace(".", "-")

    if sym.endswith("USDT"):

        return sym

    return f"{sym}USDT"





class Scanner:

    def __init__(self) -> None:

        self._lock = threading.Lock()

        self.scanning = False

        self.last_scan: str | None = None

        self.last_error: str | None = None

        self.progress = ""

        self.regimes: dict = {}

        self.watchlist: dict[str, list[dict]] = {"crypto": [], "stocks": []}

        self.bearish_context: dict[str, list[dict]] = {"crypto": [], "stocks": []}

        self.diagnostics: dict[str, dict[str, dict]] = {"crypto": {}, "stocks": {}}

        self._prev_triggered: set[str] = set()

        self._market_ctx: dict[str, dict] = {}

        self._timing_gate = TimingAlertGate()

        self._price_gate = PriceRefreshGate()



    def snapshot(self, *, refresh_prices: bool = True) -> dict:
        """Stato corrente. Con refresh_prices=True aggiorna last_price (live) sulle watchlist."""
        if refresh_prices and not self.scanning:
            # force=True: ogni poll UI deve mostrare il prezzo di mercato, non la daily chiusa
            n = self.refresh_watchlist_prices(force=True)
            if n == 0:
                log.debug("refresh prezzi: 0 aggiornati (watchlist vuota o fetch fallito)")

        with self._lock:

            return {

                "scanning": self.scanning,

                "progress": self.progress,

                "last_scan": self.last_scan,

                "last_error": self.last_error,

                "regimes": self.regimes,

                "watchlist": self.watchlist,

                "bearish_context": self.bearish_context,

            }

    def refresh_watchlist_prices(self, *, force: bool = False) -> int:
        """Aggiorna PREZZO live su crypto+stocks watchlist; riallinea status vs rottura."""
        if not self._price_gate.allow(force=force):
            return 0
        with self._lock:
            crypto = list(self.watchlist.get("crypto", []))
            stocks = list(self.watchlist.get("stocks", []))
        crypto_syms = [r["symbol"] for r in crypto]
        stock_syms = [r["symbol"] for r in stocks]
        if not crypto_syms and not stock_syms:
            return 0
        try:
            prices = fetch_live_prices(crypto_syms, stock_syms)
        except Exception as exc:
            log.warning("refresh prezzi live fallito: %s", exc)
            return 0
        if not prices:
            log.warning(
                "refresh prezzi: fetch vuoto (syms crypto=%s stocks=%s)",
                crypto_syms,
                stock_syms,
            )
            return 0
        with self._lock:
            n = 0
            n += apply_live_prices(self.watchlist.get("crypto", []), prices)
            n += apply_live_prices(self.watchlist.get("stocks", []), prices)
            if n:
                log.info("refresh prezzi live: aggiornati %d simboli", n)
        return n



    def get_diagnostics(self, market: str, symbols: list[str] | None = None) -> dict:

        with self._lock:

            cache = dict(self.diagnostics.get(market, {}))

        if symbols:

            norm = [_normalize_symbol(market, s) for s in symbols]

            cache = {k: v for k, v in cache.items() if k in norm}

        return {"market": market, "items": list(cache.values()), "symbols": list(cache.keys())}



    def get_symbol_diagnostic(self, market: str, symbol: str) -> dict | None:

        sym = _normalize_symbol(market, symbol)

        with self._lock:

            hit = self.diagnostics.get(market, {}).get(sym)

            ctx = self._market_ctx.get(market)

        if hit is not None:
            # Cache pre-FASE4 o scan senza flow: idrata OI/CVD se manca (crypto).
            if market == "crypto" and hit.get("flow") is None and ctx is not None:
                refreshed = self._diagnose_one(market, sym, ctx)
                if refreshed is None:
                    refreshed = self._fetch_and_diagnose(market, sym, ctx)
                if refreshed is not None:
                    with self._lock:
                        self.diagnostics.setdefault(market, {})[sym] = refreshed
                    return refreshed
            return hit

        if ctx is None:

            return None

        result = self._diagnose_one(market, sym, ctx)

        if result is None:

            result = self._fetch_and_diagnose(market, sym, ctx)

        if result is not None:

            with self._lock:

                self.diagnostics.setdefault(market, {})[sym] = result

        return result



    def run_scan(self) -> None:

        with self._lock:

            if self.scanning:

                return

            self.scanning = True

            self.last_error = None

        try:

            self._scan_crypto()

            self._scan_stocks()

            with self._lock:

                self.last_scan = datetime.now(timezone.utc).isoformat(timespec="seconds")

                self.progress = ""

        except Exception as exc:

            log.error("scan fallito: %s\n%s", exc, traceback.format_exc())

            with self._lock:

                self.last_error = str(exc)

        finally:

            with self._lock:

                self.scanning = False



    def _scan_crypto(self) -> None:

        self._set_progress("Crypto: scarico dati Binance...")

        btc = binance_client.klines("BTCUSDT", "1d", 400).iloc[:-1]

        regime = regime_mod.crypto_regime(btc)



        data = {}
        forming_px: dict[str, float] = {}

        for sym in binance_client.top_usdt_symbols():

            df = binance_client.klines(sym, "1d", 400)

            if len(df) >= 221:
                # PREZZO UI: close della daily in formazione (~live).
                # data[] scarta l'ultima barra per non contaminare RS/setup.
                forming_px[sym] = float(df["close"].iloc[-1])
                data[sym] = df.iloc[:-1]



        self._set_progress("Crypto: screener forza relativa...")

        scores = screener.rs_scores(data, btc)

        candidates = screener.classify_candidates(

            data, scores, True, True

        )

        # last_price dallo screener = daily chiusa (ieri); sostituisci subito
        for c in candidates:
            px = forming_px.get(c["symbol"])
            if px is not None:
                c["last_price"] = px

        # FASE 2: regime non filtra più (banner informativo). Long-only operativo.

        long_cands = [c for c in candidates if c["direction"] == "long"]

        short_cands = [c for c in candidates if c["direction"] == "short"]



        self._set_progress("Crypto: rilevamento setup...")

        rows, all_with_setup = self._detect_setups("crypto", long_cands, data)

        _, short_setups = self._detect_setups("crypto", short_cands, data)

        bearish = [

            {

                "symbol": r["symbol"],

                "rs_score": r["rs_score"],

                "rvol": r["rvol"],

                "last_price": r["last_price"],

                "setup": r["setup"],

                "note": "Contesto ribassista — solo informativo, nessun livello operativo",

            }

            for r in short_setups

        ]



        for row in rows[:MAX_4H_CHECKS]:

            df4 = binance_client.klines(row["symbol"], "4h", 200)

            if not df4.empty:

                hist4 = df4.iloc[:-1]

                row["status"] = trigger_status_4h(

                    hist4, row["direction"], row["entry_trigger"]

                )

                c4 = detect_compression(hist4, "long", "4H")

                if c4:

                    row["tf_4h"] = {

                        "squeeze": True,

                        "entry_trigger": c4["entry_trigger"],

                        "stop": c4["stop"],

                        "note": c4["note"],

                    }

                else:

                    row["tf_4h"] = {"squeeze": False}

            fr = binance_client.funding_rate(row["symbol"])

            apply_funding_to_row(row, fr)



        # FASE 3: entry 4H — candidati long senza setup daily ma con compressione 4H

        wl_syms = {r["symbol"] for r in rows}

        for cand in long_cands:

            if cand["symbol"] in wl_syms or len(rows) >= WATCHLIST_SIZE:

                continue

            df4 = binance_client.klines(cand["symbol"], "4h", 200)

            if df4.empty:

                continue

            c4 = detect_compression(closed_klines(df4), "long", "4H")

            if c4 is None:

                continue

            row = {

                "market": "crypto",

                "symbol": cand["symbol"],

                "direction": "long",

                "rs_score": cand["rs_score"],

                "rvol": cand["rvol"],

                "last_price": cand["last_price"],

                "setup": "B",

                "entry_trigger": c4["entry_trigger"],

                "stop": c4["stop"],

                "atr": c4["atr"],

                "status": "watch",

                "note": c4["note"],

                "funding": None,

                "warnings": [],

                "entry_tf": "4H",

                "tf_4h": {

                    "squeeze": True,

                    "entry_trigger": c4["entry_trigger"],

                    "stop": c4["stop"],

                    "note": c4["note"],

                },

            }

            fr = binance_client.funding_rate(cand["symbol"])

            apply_funding_to_row(row, fr)

            rows.append(row)

            wl_syms.add(cand["symbol"])



        # Timing 1H/15m solo su watchlist (nessun alert autonomo)

        self._set_progress("Crypto: timing 1H/15m su watchlist...")

        for row in rows:

            row.setdefault("entry_tf", "D")

            lower: dict = {}

            for tf, interval in (("1H", "1h"), ("15m", "15m")):

                raw = binance_client.klines(row["symbol"], interval, 300)

                if not raw.empty:

                    lower[tf] = raw

            timing = attach_timing_to_row(row, lower, direction="long")

            row["timing"] = timing

            for t in timing:

                if not t.get("aligned_with_daily"):

                    continue

                if not self._timing_gate.allow(row["symbol"]):

                    break

                notify(

                    "crypto",

                    row["symbol"],

                    f"{row['symbol']} timing: compressione {t['timeframe']} sopra "

                    f"livello daily {row['entry_trigger']} "
                    f"(rottura {t['entry_trigger']}, invalidazione {t['stop']})",

                )

                break  # una sola notifica timing per asset in questo scan



        # FASE 4: OI + CVD su watchlist crypto (sintesi frecce; diagnostica userà lo stesso snap)

        self._set_progress("Crypto: OI/CVD su watchlist...")

        for row in rows:

            enrich_row_with_flow(row)



        # PREZZO UI = ticker futures USDT-M (non close daily spot/ieri)
        self._set_progress("Crypto: aggiorno prezzi live futures...")
        n_live = stamp_live_prices(rows, "crypto")
        if n_live < len(rows):
            for row in rows:
                if row.get("price_live"):
                    continue
                fut = binance_client.futures_klines(
                    row["symbol"], "1d", 3, use_cache=False
                )
                if fut is not None and not fut.empty:
                    row["last_price"] = float(fut["close"].iloc[-1])
                    row["price_live"] = True
            still = sum(1 for r in rows if not r.get("price_live"))
            if still:
                log.warning(
                    "crypto prezzi futures: %d/%d senza ticker (fallback spot forming)",
                    still,
                    len(rows),
                )
                for row in rows:
                    if row.get("price_live"):
                        continue
                    px = forming_px.get(row["symbol"])
                    if px is not None:
                        row["last_price"] = px

        # FASE 5: confluence solo ordinamento (mai esclusione)

        for row in rows:

            attach_confluence(row)

            row["scenario_ids"] = scenario_ids_for_row(row, flow=row.get("_flow_snap"))

        rows = sort_by_confluence(rows)



        ctx = {

            "regime": regime,

            "data": data,

            "scores": scores,

            "candidates": candidates,

            "all_with_setup": all_with_setup,

            "bench": btc,

            "flow_by_symbol": {r["symbol"]: r.get("_flow_snap") for r in rows if r.get("_flow_snap")},

        }

        self._build_diagnostics_cache("crypto", ctx, rows)

        self._finalize("crypto", regime, rows, bearish)



    def _scan_stocks(self) -> None:

        self._set_progress("Stocks: scarico universo S&P500 + Nasdaq100...")

        universe = stocks_client.stock_universe()

        bench = stocks_client.daily_history(["SPY", "QQQ", "^VIX"], threads=False, min_bars=50)

        spy, qqq = bench.get("SPY"), bench.get("QQQ")

        vix_df = bench.get("^VIX")

        vix_last = float(vix_df["close"].iloc[-1]) if vix_df is not None else None

        if spy is None or qqq is None:

            raise RuntimeError("dati SPY/QQQ non disponibili da Yahoo Finance")

        regime = regime_mod.stock_regime(spy, qqq, vix_last)



        self._set_progress(f"Stocks: scarico storico daily di {len(universe)} titoli (1-2 min)...")

        data_all = stocks_client.daily_history(universe)



        data = {}

        for sym, df in data_all.items():

            last = float(df["close"].iloc[-1])

            avg_vol = float(df["volume"].rolling(20).mean().iloc[-1])

            if last < STOCK_MIN_PRICE or avg_vol < STOCK_MIN_AVG_VOLUME:

                continue

            if adr_pct(df) < STOCK_MIN_ADR_PCT:

                continue

            data[sym] = df



        self._set_progress("Stocks: screener forza relativa...")

        scores = screener.rs_scores(data, spy)

        candidates = screener.classify_candidates(

            data, scores, True, True

        )

        # FASE 2: regime/halt non bloccano la watchlist (banner informativo).

        long_cands = [c for c in candidates if c["direction"] == "long"]

        short_cands = [c for c in candidates if c["direction"] == "short"]



        self._set_progress("Stocks: rilevamento setup...")

        rows, all_with_setup = self._detect_setups("stocks", long_cands, data)

        _, short_setups = self._detect_setups("stocks", short_cands, data)

        bearish = [

            {

                "symbol": r["symbol"],

                "rs_score": r["rs_score"],

                "rvol": r["rvol"],

                "last_price": r["last_price"],

                "setup": r["setup"],

                "note": "Contesto ribassista — solo informativo, nessun livello operativo",

            }

            for r in short_setups

        ]



        for row in rows[:MAX_4H_CHECKS]:

            df4 = stocks_client.intraday_4h(row["symbol"])

            if not df4.empty:

                row["status"] = trigger_status_4h(df4, row["direction"], row["entry_trigger"])



        # PREZZO = quotazione di mercato corrente (non chiusura daily/4H degli indicatori)
        self._set_progress("Stocks: aggiorno prezzi live...")
        stamp_live_prices(rows, "stocks")

        for row in rows:

            attach_confluence(row)

            row["scenario_ids"] = scenario_ids_for_row(row)

        rows = sort_by_confluence(rows)



        ctx = {

            "regime": regime,

            "data": data,

            "scores": scores,

            "candidates": candidates,

            "all_with_setup": all_with_setup,

            "bench": spy,

        }

        self._build_diagnostics_cache("stocks", ctx, rows)

        self._finalize("stocks", regime, rows, bearish)



    def _detect_setups(

        self, market: str, candidates: list[dict], data: dict

    ) -> tuple[list[dict], list[dict]]:

        rows: list[dict] = []

        all_with_setup: list[dict] = []

        for cand in candidates:

            df = data[cand["symbol"]]

            setup = detect_setup_a(df, cand["direction"], market) or detect_setup_b(
                df, cand["direction"], market
            )

            if setup is None:

                continue

            row = {

                "market": market,

                "symbol": cand["symbol"],

                "direction": cand["direction"],

                "rs_score": cand["rs_score"],

                "rvol": cand["rvol"],

                "last_price": cand["last_price"],

                "setup": setup["setup"],

                "entry_trigger": setup["entry_trigger"],

                "stop": setup["stop"],

                "atr": setup["atr"],

                "status": setup.get("status_hint", "watch"),

                "note": setup["note"],

                "funding": None,

                "warnings": [],

            }

            all_with_setup.append(row)

            if len(rows) < WATCHLIST_SIZE:

                rows.append(row)

        return rows, all_with_setup



    def _diagnose_symbols_for_market(self, market: str, ctx: dict, watchlist_rows: list[dict]) -> dict[str, dict]:

        regime = ctx["regime"]

        data: dict = ctx["data"]

        scores: dict = ctx["scores"]

        candidates = ctx["candidates"]

        all_with_setup = ctx.get("all_with_setup", [])



        cand_map = {c["symbol"]: c for c in candidates}

        wl_symbols = {r["symbol"] for r in watchlist_rows}

        setup_symbols = {r["symbol"] for r in all_with_setup}

        capped_symbols = setup_symbols - wl_symbols



        if market == "crypto":

            sym_set = set(data.keys())

        else:

            ranked = sorted(scores.items(), key=lambda x: abs(x[1] - 0.5), reverse=True)

            sym_set = {s for s, _ in ranked[:DIAG_TOP_N]}

            sym_set |= wl_symbols

            sym_set |= setup_symbols



        watchlist_eligible = set(cand_map.keys())

        if market == "crypto" and regime.get("mode") == "mixed":

            watchlist_eligible = {s for s in watchlist_eligible if s in ("BTCUSDT", "ETHUSDT")}



        out: dict[str, dict] = {}

        flow_by = ctx.get("flow_by_symbol") or {}

        for sym in sym_set:

            if sym not in data:

                continue

            snap = flow_by.get(sym)

            # Diagnostica: OI/CVD per ogni crypto in cache (non solo watchlist).
            # La watchlist resta la sola a ricevere enrich in scan; qui idratiamo on-demand.
            if market == "crypto" and snap is None:

                try:

                    snap = fetch_flow_snapshot(sym)

                except Exception:

                    snap = None

            out[sym] = diagnose_asset(

                market,

                sym,

                data[sym],

                regime,

                scores.get(sym),

                on_watchlist=sym in wl_symbols,

                watchlist_eligible=sym in watchlist_eligible,

                mixed_filtered=(

                    market == "crypto"

                    and regime.get("mode") == "mixed"

                    and sym not in ("BTCUSDT", "ETHUSDT")

                ),

                capped_out=sym in capped_symbols,

                flow_snap=snap if market == "crypto" else None,

            )

        return out



    def _diagnose_one(self, market: str, symbol: str, ctx: dict) -> dict | None:

        data = ctx.get("data", {})

        if symbol not in data:

            return None

        return self._build_asset_diagnostic(market, symbol, ctx, data)



    def _fetch_and_diagnose(self, market: str, symbol: str, ctx: dict) -> dict | None:

        data = dict(ctx.get("data", {}))

        bench = ctx.get("bench")

        try:

            if market == "crypto":

                if symbol not in data:

                    df = binance_client.klines(symbol, "1d", 400)

                    if len(df) < 221:

                        return None

                    data[symbol] = df.iloc[:-1]

                if bench is None:

                    bench = binance_client.klines("BTCUSDT", "1d", 400).iloc[:-1]

            else:

                if symbol not in data:

                    fetched = stocks_client.daily_history([symbol], threads=False, min_bars=220)

                    if symbol not in fetched or len(fetched[symbol]) < 220:

                        return None

                    data[symbol] = fetched[symbol]

                if bench is None:

                    return None

        except Exception as exc:

            log.warning("fetch on-demand %s/%s fallito: %s", market, symbol, exc)

            return None



        scores = screener.rs_scores(data, bench)

        ctx = {**ctx, "data": data, "scores": scores, "candidates": screener.classify_candidates(

            data, scores, ctx["regime"]["long_allowed"], ctx["regime"]["short_allowed"]

        )}

        return self._build_asset_diagnostic(market, symbol, ctx, data)



    def _build_asset_diagnostic(self, market: str, symbol: str, ctx: dict, data: dict) -> dict:

        regime = ctx["regime"]

        scores = ctx.get("scores", {})

        candidates = ctx.get("candidates", [])

        all_with_setup = ctx.get("all_with_setup", [])

        wl_rows = self.watchlist.get(market, [])

        wl_symbols = {r["symbol"] for r in wl_rows}

        setup_symbols = {r["symbol"] for r in all_with_setup}

        cand_map = {c["symbol"]: c for c in candidates}

        watchlist_eligible = set(cand_map.keys())

        if market == "crypto" and regime.get("mode") == "mixed":

            watchlist_eligible = {s for s in watchlist_eligible if s in ("BTCUSDT", "ETHUSDT")}



        snap = None
        if market == "crypto":
            snap = (ctx.get("flow_by_symbol") or {}).get(symbol)
            if snap is None:
                for r in wl_rows:
                    if r.get("symbol") == symbol and r.get("_flow_snap"):
                        snap = r["_flow_snap"]
                        break
            if snap is None:
                try:
                    snap = fetch_flow_snapshot(symbol)
                except Exception:
                    snap = None

        return diagnose_asset(

            market,

            symbol,

            data[symbol],

            regime,

            scores.get(symbol),

            on_watchlist=symbol in wl_symbols,

            watchlist_eligible=symbol in watchlist_eligible,

            mixed_filtered=(

                market == "crypto"

                and regime.get("mode") == "mixed"

                and symbol not in ("BTCUSDT", "ETHUSDT")

            ),

            capped_out=symbol in setup_symbols and symbol not in wl_symbols,

            flow_snap=snap,

        )



    def _build_diagnostics_cache(self, market: str, ctx: dict, watchlist_rows: list[dict]) -> None:

        diag = self._diagnose_symbols_for_market(market, ctx, watchlist_rows)

        # Allinea PREZZO diagnostica al live già stampato sulla watchlist,
        # preservando close D (filtri) come campo separato.
        for row in watchlist_rows:
            sym = row.get("symbol")
            if sym and sym in diag and row.get("last_price") is not None:
                if row.get("price_live"):
                    diag[sym]["last_price"] = row["last_price"]
                    diag[sym]["price_live"] = True
                    diag[sym]["price_kind"] = "live"
                    diag[sym]["price_asof"] = row.get("price_asof")
                else:
                    diag[sym]["last_price"] = row["last_price"]
                    diag[sym]["price_asof"] = row.get("price_asof") or diag[sym].get("close_d_asof")
                    diag[sym]["price_kind"] = diag[sym].get("price_kind") or "close_d"

        with self._lock:

            self.diagnostics[market] = diag

            self._market_ctx[market] = ctx



    def _finalize(

        self, market: str, regime: dict, rows: list[dict], bearish: list[dict] | None = None

    ) -> None:

        # Ultimo passo obbligatorio: PREZZO = quotazione live (crypto futures / stocks Yahoo).
        # Non fidarsi di last_price dallo screener (daily chiusa = ieri).
        try:
            n = stamp_live_prices(rows, market)
            log.info("finalize %s: stamp live prices %d/%d", market, n, len(rows))
        except Exception as exc:
            log.warning("finalize %s: stamp live prices fallito: %s", market, exc)

        for row in rows:

            if row.get("direction") != "long":

                continue  # nessun alert su contesto ribassista

            key = f"{market}:{row['symbol']}:{row['direction']}:{row['setup']}"

            if row["status"] == "triggered" and key not in self._prev_triggered:

                setup_label = (

                    "pullback" if row["setup"] == "A" else "compressione/breakout"

                )

                fr = row.get("funding")

                if fr is None:

                    fund_txt = "funding n/d"

                elif abs(fr) < 0.0001:

                    fund_txt = "funding neutro"

                else:

                    fund_txt = f"funding {(fr * 100):.4f}%/8h"

                rs = row.get("rs_score")

                rs_txt = f"RS {rs:.0%}" if isinstance(rs, (int, float)) else "RS n/d"

                notify(

                    market,

                    row["symbol"],

                    f"{row['symbol']} entra in watchlist: {setup_label} + {rs_txt}, "

                    f"rottura {row['entry_trigger']}, invalidazione {row['stop']}, {fund_txt}",

                )

                if PLAYBOOK_IN_ALERTS:

                    card = primary_alert_scenario(row, flow=row.get("_flow_snap"))

                    if card and card.get("monitorare"):

                        notify(

                            market,

                            row["symbol"],

                            f"[scenario] {card['titolo']} — verifica: {card['monitorare'][0]}",

                        )

            if row["status"] == "triggered":

                self._prev_triggered.add(key)

        with self._lock:

            self.regimes[market] = regime

            # Non esporre snap interno nella state API
            clean = []
            for r in rows:
                row = {k: v for k, v in r.items() if k != "_flow_snap"}
                clean.append(row)
            self.watchlist[market] = clean

            self.bearish_context[market] = bearish or []



    def _set_progress(self, msg: str) -> None:

        with self._lock:

            self.progress = msg

        log.info(msg)





scanner = Scanner()


