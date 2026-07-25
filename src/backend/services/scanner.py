"""Scanner: orchestra regime -> screener -> setup -> watchlist -> alert."""

import logging

import threading

import traceback

from datetime import datetime, timezone



from config import (
    FUNDING_BLOCK,
    FUNDING_EXTREME,
    STOCK_MIN_ADR_PCT,
    STOCK_MIN_AVG_VOLUME,
    STOCK_MIN_PRICE,
    WATCHLIST_SIZE,
)

from data import binance_client, stocks_client

from engine import regime as regime_mod

from engine import screener

from engine.diagnostics import diagnose_asset

from engine.indicators import adr_pct

from engine.setups import detect_setup_a, detect_setup_b, trigger_status_4h

from services.alerts import notify



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

        self.diagnostics: dict[str, dict[str, dict]] = {"crypto": {}, "stocks": {}}

        self._prev_triggered: set[str] = set()

        self._market_ctx: dict[str, dict] = {}



    def snapshot(self) -> dict:

        with self._lock:

            return {

                "scanning": self.scanning,

                "progress": self.progress,

                "last_scan": self.last_scan,

                "last_error": self.last_error,

                "regimes": self.regimes,

                "watchlist": self.watchlist,

            }



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

        for sym in binance_client.top_usdt_symbols():

            df = binance_client.klines(sym, "1d", 400)

            if len(df) >= 221:

                data[sym] = df.iloc[:-1]



        self._set_progress("Crypto: screener forza relativa...")

        scores = screener.rs_scores(data, btc)

        candidates = screener.classify_candidates(

            data, scores, regime["long_allowed"], regime["short_allowed"]

        )

        if regime["mode"] == "mixed":

            candidates = [c for c in candidates if c["symbol"] in ("BTCUSDT", "ETHUSDT")]



        self._set_progress("Crypto: rilevamento setup...")

        rows, all_with_setup = self._detect_setups("crypto", candidates, data)



        for row in rows[:MAX_4H_CHECKS]:

            df4 = binance_client.klines(row["symbol"], "4h", 200)

            if not df4.empty:

                row["status"] = trigger_status_4h(

                    df4.iloc[:-1], row["direction"], row["entry_trigger"]

                )

            fr = binance_client.funding_rate(row["symbol"])

            apply_funding_to_row(row, fr)



        ctx = {

            "regime": regime,

            "data": data,

            "scores": scores,

            "candidates": candidates,

            "all_with_setup": all_with_setup,

            "bench": btc,

        }

        self._build_diagnostics_cache("crypto", ctx, rows)

        self._finalize("crypto", regime, rows)



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

            data, scores, regime["long_allowed"], regime["short_allowed"]

        )

        if regime["mode"] == "halt":

            candidates = []



        self._set_progress("Stocks: rilevamento setup...")

        rows, all_with_setup = self._detect_setups("stocks", candidates, data)



        for row in rows[:MAX_4H_CHECKS]:

            df4 = stocks_client.intraday_4h(row["symbol"])

            if not df4.empty:

                row["status"] = trigger_status_4h(df4, row["direction"], row["entry_trigger"])



        ctx = {

            "regime": regime,

            "data": data,

            "scores": scores,

            "candidates": candidates,

            "all_with_setup": all_with_setup,

            "bench": spy,

        }

        self._build_diagnostics_cache("stocks", ctx, rows)

        self._finalize("stocks", regime, rows)



    def _detect_setups(

        self, market: str, candidates: list[dict], data: dict

    ) -> tuple[list[dict], list[dict]]:

        rows: list[dict] = []

        all_with_setup: list[dict] = []

        for cand in candidates:

            df = data[cand["symbol"]]

            setup = detect_setup_a(df, cand["direction"]) or detect_setup_b(df, cand["direction"])

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

        for sym in sym_set:

            if sym not in data:

                continue

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

        )



    def _build_diagnostics_cache(self, market: str, ctx: dict, watchlist_rows: list[dict]) -> None:

        diag = self._diagnose_symbols_for_market(market, ctx, watchlist_rows)

        with self._lock:

            self.diagnostics[market] = diag

            self._market_ctx[market] = ctx



    def _finalize(self, market: str, regime: dict, rows: list[dict]) -> None:

        for row in rows:

            key = f"{market}:{row['symbol']}:{row['direction']}:{row['setup']}"

            if row["status"] == "triggered" and key not in self._prev_triggered:

                notify(

                    market,

                    row["symbol"],

                    f"TRIGGER Setup {row['setup']} {row['direction'].upper()} — "

                    f"entrata {row['entry_trigger']}, stop {row['stop']}. "

                    f"Verifica su TradingView e usa il Trade Planner.",

                )

            if row["status"] == "triggered":

                self._prev_triggered.add(key)

        with self._lock:

            self.regimes[market] = regime

            self.watchlist[market] = rows



    def _set_progress(self, msg: str) -> None:

        with self._lock:

            self.progress = msg

        log.info(msg)





scanner = Scanner()


