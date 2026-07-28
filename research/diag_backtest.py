"""Diagnosi del backtester (7 punti) — nessuna modifica a setup o parametri.

Esegue su BTCUSDT+ETHUSDT dal 2022 (come il run originale):
1. log per-trade CSV con MAE/MFE in R;
2. ambiguità intra-barra: pessimistica / ottimistica / esclusione;
3. stop sulla barra di entry: conteggio + variante disattivata;
4. benchmark random (500 sim, stop 1xATR, target 2R, stessi costi);
5. audit funnel screener/regime + rerun senza gate RS;
6. verifica costi su 5 trade campione;
7. rerun su universo top-30 crypto (tabella IS/OOS).

Uso (dalla root del repo):
  python research/diag_backtest.py            (punti 1-6)
  python research/diag_backtest.py --top30    (aggiunge il punto 7, piu' lento)
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1] / "src" / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

import numpy as np
import pandas as pd

from data import binance_client
from engine.backtest import (
    MIN_BARS,
    Trade,
    _Position,
    _close_trade,
    aggregate,
    aggregate_by,
    build_production_signal_fn,
    check_exit,
    simulate_symbol,
    trades_to_csv,
    wilson_ci,
)
from engine.indicators import atr, ema
from engine.screener import classify_candidates, rs_scores
from engine.setups import detect_setup_a, detect_setup_b, setup_a_metrics, setup_b_metrics

START = pd.Timestamp("2022-01-01", tz="UTC")
SPLIT = pd.Timestamp("2025-01-01", tz="UTC")
WARMUP_MS = int((START - pd.Timedelta(days=400)).timestamp() * 1000)
CAPITAL, RISK_PCT = 10_000.0, 1.0


def sep(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def row(label: str, trades: list[Trade]) -> str:
    a = aggregate(trades)
    if a.get("n_trades", 0) == 0:
        return f"{label:38s} n=   0  —"
    lo, hi = a["win_rate_ci95"]
    pf = a["profit_factor"]
    pf_s = f"{pf:.3f}" if pf != float("inf") else "inf"
    return (
        f"{label:38s} n={a['n_trades']:4d}  WR={a['win_rate']*100:5.1f}% "
        f"(CI {lo*100:.1f}-{hi*100:.1f}%)  exp={a['expectancy_r']:+.3f}R  "
        f"PF={pf_s}  DD={a['max_drawdown_r']:.2f}R"
    )


def load_data(symbols: list[str]) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    data: dict[str, pd.DataFrame] = {}
    for sym in symbols:
        df = binance_client.klines_range(sym, "1d", WARMUP_MS)
        if len(df) > MIN_BARS:
            data[sym] = df.iloc[:-1]
    bench = data.get("BTCUSDT")
    if bench is None:
        bench = binance_client.klines_range("BTCUSDT", "1d", WARMUP_MS).iloc[:-1]
    return data, bench


def run_variant(
    data: dict[str, pd.DataFrame],
    bench: pd.DataFrame,
    *,
    ambiguous_policy: str = "pessimistic",
    entry_bar_stop: bool = True,
    signal_builder=None,
) -> list[Trade]:
    builder = signal_builder or (lambda s, d, b: build_production_signal_fn(s, d, b))
    trades: list[Trade] = []
    for sym, df in data.items():
        fn = builder(sym, data, bench)
        trades.extend(
            simulate_symbol(
                df, fn, market="crypto", symbol=sym, capital=CAPITAL,
                risk_pct=RISK_PCT, start=START,
                ambiguous_policy=ambiguous_policy, entry_bar_stop=entry_bar_stop,
            )
        )
    trades.sort(key=lambda t: t.entry_date)
    return trades


# ---------------------------------------------------------------------------
# Cache candidati per data (identica semantica di build_production_signal_fn)
# ---------------------------------------------------------------------------


def build_candidate_cache(
    data: dict[str, pd.DataFrame], bench: pd.DataFrame
) -> dict[pd.Timestamp, dict[str, str]]:
    all_dates = sorted({d for df in data.values() for d in df.index if d >= START})
    cache: dict[pd.Timestamp, dict[str, str]] = {}
    for date in all_dates:
        slices = {s: d.loc[d.index < date] for s, d in data.items()}
        slices = {s: d for s, d in slices.items() if len(d) >= MIN_BARS}
        bench_slice = bench.loc[bench.index < date]
        if not slices or len(bench_slice) < MIN_BARS:
            cache[date] = {}
            continue
        scores = rs_scores(slices, bench_slice)
        cands = classify_candidates(slices, scores, True, True)
        cache[date] = {c["symbol"]: c["direction"] for c in cands}
    return cache


def build_cached_signal_builder(cand_cache: dict):
    def builder(symbol: str, data: dict, bench: pd.DataFrame):
        def fn(hist: pd.DataFrame, date: pd.Timestamp):
            direction = cand_cache.get(date, {}).get(symbol)
            if direction is None or len(hist) < MIN_BARS:
                return None
            setup = detect_setup_a(hist, direction) or detect_setup_b(hist, direction)
            if setup is None:
                return None
            return {**setup, "direction": direction}
        return fn
    return builder


def build_trend_only_signal_builder():
    """Screener senza gate RS percentile: resta solo il filtro trend EMA50."""
    def builder(symbol: str, data: dict, bench: pd.DataFrame):
        df = data[symbol]
        def fn(hist: pd.DataFrame, date: pd.Timestamp):
            if len(hist) < MIN_BARS:
                return None
            last = float(hist["close"].iloc[-1])
            e50 = float(ema(hist["close"], 50).iloc[-1])
            direction = "long" if last > e50 else "short"
            setup = detect_setup_a(hist, direction) or detect_setup_b(hist, direction)
            if setup is None:
                return None
            return {**setup, "direction": direction}
        return fn
    return builder


# ---------------------------------------------------------------------------
# Punto 1 — log per-trade + MAE/MFE
# ---------------------------------------------------------------------------


def point1(base: list[Trade]) -> None:
    sep("PUNTO 1 — Log per-trade (backtest_trades.csv) + MAE/MFE")
    trades_to_csv(base, "backtest_trades.csv")
    print(f"CSV scritto: backtest_trades.csv ({len(base)} trade)")
    losers = [t for t in base if t.r_net <= 0]
    winners = [t for t in base if t.r_net > 0]
    print(f"\nNota metodo: MFE/MAE usano gli estremi delle barre INTERE tra entry")
    print("ed exit; la barra di uscita contribuisce solo col prezzo di uscita")
    print("(stima conservativa: l'ordine intra-barra non è conoscibile sul daily).")
    if losers:
        mfe_losers = [t.mfe_r for t in losers]
        print(f"\nPerdenti: {len(losers)}")
        print(f"  MFE mediana : {statistics.median(mfe_losers):+.2f}R")
        print(f"  MFE media   : {statistics.mean(mfe_losers):+.2f}R")
        print(f"  MFE max     : {max(mfe_losers):+.2f}R")
        over_1r = sum(1 for m in mfe_losers if m >= 1.0)
        over_05 = sum(1 for m in mfe_losers if m >= 0.5)
        print(f"  perdenti con MFE >= 1.0R: {over_1r}/{len(losers)}")
        print(f"  perdenti con MFE >= 0.5R: {over_05}/{len(losers)}")
    if winners:
        mae_winners = [t.mae_r for t in winners]
        print(f"\nVincenti: {len(winners)}")
        print(f"  MAE mediana : {statistics.median(mae_winners):.2f}R")
        print(f"  MAE max     : {max(mae_winners):.2f}R")
    print("\nDettaglio trade:")
    for t in base:
        print(
            f"  {t.entry_date.date()} {t.symbol:9s} {t.setup} {t.direction:5s} "
            f"sig={t.signal_date.date() if t.signal_date is not None else '?'} "
            f"in={t.entry:.6g} out={t.exit:.6g} ({t.exit_reason:13s}) "
            f"R={t.r_net:+.2f} MAE={t.mae_r:.2f} MFE={t.mfe_r:+.2f}"
            f"{' AMB' if t.exit_ambiguous else ''}"
        )


# ---------------------------------------------------------------------------
# Punto 2 — ambiguità intra-barra
# ---------------------------------------------------------------------------


def point2(data, bench, base: list[Trade]) -> None:
    sep("PUNTO 2 — Ambiguità intra-barra (high>=target E low<=stop)")
    print("Risoluzione attuale del simulatore (ordine dei check, direzione long):")
    print("  1. open <= stop            -> uscita all'open (stop_gap)")
    print("  2. low<=stop E high>=target-> barra AMBIGUA: default vince lo STOP")
    print("  3. low <= stop             -> uscita allo stop")
    print("  4. open >= target          -> uscita all'open (target_gap)")
    print("  5. high >= target          -> uscita al target")
    print("Sulla barra di ENTRY viene valutato solo lo stop (mai il target),")
    print("quindi anche l'entry-bar può essere ambigua (stop preso, target ignorato).")

    amb = [t for t in base if t.exit_ambiguous]
    print(f"\nTrade con barra di uscita ambigua: {len(amb)}/{len(base)}")
    for t in amb:
        print(f"  {t.entry_date.date()} {t.symbol} {t.setup} exit={t.exit_reason} R={t.r_net:+.2f}")

    optimistic = run_variant(data, bench, ambiguous_policy="optimistic")
    excluded = [t for t in base if not t.exit_ambiguous]
    print()
    print(row("(a) pessimistica (stop prima)", base))
    print(row("(b) ottimistica (target prima)", optimistic))
    print(row("(c) esclusi trade ambigui", excluded))


# ---------------------------------------------------------------------------
# Punto 3 — stop sulla barra di entry
# ---------------------------------------------------------------------------


def point3(data, bench, base: list[Trade]) -> None:
    sep("PUNTO 3 — Stop sulla barra di entry")
    same_bar = [t for t in base if t.exit_reason in ("stop_same_bar", "target_same_bar")]
    print("Sì: il simulatore valuta lo stop già sulla barra che filla l'entry")
    print("(direzione long: se low <= stop dopo il fill, chiusura a -1R).")
    print(f"\nTrade morti nella barra di ingresso: {len(same_bar)}/{len(base)}")
    for t in same_bar:
        print(f"  {t.entry_date.date()} {t.symbol} {t.setup} in={t.entry:.6g} stop={t.stop:.6g}")

    no_entry_stop = run_variant(data, bench, entry_bar_stop=False)
    print()
    print(row("baseline (stop attivo su entry-bar)", base))
    print(row("variante (stop da open barra dopo)", no_entry_stop))


# ---------------------------------------------------------------------------
# Punto 4 — benchmark random
# ---------------------------------------------------------------------------


def _simulate_fixed_trade(
    df: pd.DataFrame, i: int, entry: float, stop: float, target: float
) -> Trade | None:
    from engine.sizing import position_size

    risk_per_unit = entry - stop
    if risk_per_unit <= 0:
        return None
    sizing = position_size(CAPITAL, RISK_PCT, entry, stop, direction="long", market="crypto")
    if "error" in sizing:
        return None
    pos = _Position(
        symbol="RND", setup="R", direction="long", entry_date=df.index[i],
        entry=entry, stop=stop, target=target, risk_per_unit=risk_per_unit,
        size_units=float(sizing["size_units"]), risk_amount=float(sizing["risk_amount"]),
        notional=float(sizing["notional"]),
    )
    # stessa regola della strategia: stop valutato già sulla barra di entry
    if float(df["low"].iloc[i]) <= stop:
        return _close_trade(pos, stop, "stop_same_bar", df.index[i], "crypto", {})
    for j in range(i + 1, len(df)):
        pos.bars_held += 1
        hit = check_exit(df.iloc[j], pos, None)
        if hit is not None:
            return _close_trade(pos, hit[0], hit[1], df.index[j], "crypto", {})
    return _close_trade(pos, float(df["close"].iloc[-1]), "eof", df.index[-1], "crypto", {})


def point4(data, base: list[Trade], n_sims: int = 500, seed: int = 42) -> None:
    sep("PUNTO 4 — Benchmark random (500 sim, stop 1xATR, target 2R, stessi costi)")
    rng = np.random.default_rng(seed)
    atr_series = {sym: atr(df) for sym, df in data.items()}
    pool: list[tuple[str, int]] = []
    for sym, df in data.items():
        for i in range(MIN_BARS, len(df) - 1):
            if df.index[i] >= START:
                pool.append((sym, i))
    n_trades = max(len(base), 1)
    print(f"Pool: {len(pool)} barre candidabili, {n_trades} entry per simulazione,")
    print("entry all'open della barra estratta, direzione LONG (come i trade reali),")
    print("stessa regola same-bar stop e stessi costi (fee taker + funding).")

    wrs, exps = [], []
    for _ in range(n_sims):
        picks = rng.choice(len(pool), size=n_trades, replace=True)
        rs = []
        for k in picks:
            sym, i = pool[int(k)]
            df = data[sym]
            a = float(atr_series[sym].iloc[i - 1])
            if not np.isfinite(a) or a <= 0:
                continue
            entry = float(df["open"].iloc[i])
            t = _simulate_fixed_trade(df, i, entry, entry - a, entry + 2 * a)
            if t is not None:
                rs.append(t.r_net)
        if rs:
            wrs.append(sum(1 for r in rs if r > 0) / len(rs))
            exps.append(sum(rs) / len(rs))

    strat = aggregate(base)
    wr_s, exp_s = strat["win_rate"], strat["expectancy_r"]
    print(f"\nRandom  WR: media={np.mean(wrs)*100:.1f}%  p5={np.percentile(wrs,5)*100:.1f}%  "
          f"mediana={np.percentile(wrs,50)*100:.1f}%  p95={np.percentile(wrs,95)*100:.1f}%")
    print(f"Random exp: media={np.mean(exps):+.3f}R  p5={np.percentile(exps,5):+.3f}R  "
          f"mediana={np.percentile(exps,50):+.3f}R  p95={np.percentile(exps,95):+.3f}R")
    print(f"\nStrategia: WR={wr_s*100:.1f}%  exp={exp_s:+.3f}R")
    frac_wr = np.mean([w <= wr_s for w in wrs])
    frac_exp = np.mean([e <= exp_s for e in exps])
    print(f"Quota di simulazioni random con WR  <= strategia: {frac_wr*100:.1f}%")
    print(f"Quota di simulazioni random con exp <= strategia: {frac_exp*100:.1f}%")

    print("\n10 trade peggiori della strategia (da ispezionare sul chart):")
    for t in sorted(base, key=lambda t: t.r_net)[:10]:
        print(
            f"  {t.entry_date.date()} -> {t.exit_date.date()} {t.symbol:9s} {t.setup} "
            f"{t.direction} in={t.entry:.6g} stop={t.stop:.6g} out={t.exit:.6g} "
            f"({t.exit_reason}) R={t.r_net:+.2f} MFE={t.mfe_r:+.2f}"
        )


# ---------------------------------------------------------------------------
# Punto 5 — audit funnel screener/regime
# ---------------------------------------------------------------------------


def point5(data, bench) -> list[Trade]:
    sep("PUNTO 5 — Audit funnel screener/regime + rerun senza gate RS")
    print("Filtri NON applicati nel backtest (dichiarato nel codice):")
    print("  - regime di mercato: long e short sempre consentiti -> scarti: 0")
    print("  - conferma 4H con volume: l'entry usa la rottura del trigger sul")
    print("    daily successivo, non lo stato 4H -> scarti: 0")
    print("Il gate attivo è: screener RS percentile + trend EMA50 (classify_candidates).")

    cand_cache = build_candidate_cache(data, bench)
    counters = {
        "raw_a": 0, "raw_b": 0, "geo_a": 0, "geo_b": 0,
        "signals": 0, "rs_pass": 0, "rs_discard": 0, "filled": 0, "unfilled": 0,
    }
    for sym, df in data.items():
        for i in range(MIN_BARS, len(df)):
            date = df.index[i]
            if date < START:
                continue
            hist = df.iloc[:i]
            cand_dir = cand_cache.get(date, {}).get(sym)
            for direction in ("long", "short"):
                ma = setup_a_metrics(hist, direction)
                a_core = bool(ma and ma["aligned"] and ma["in_zone"]
                              and ma["momentum_ok"] and ma["vol_declining"])
                a_valid = a_core and ma["stop_geometry_ok"]
                if a_core:
                    counters["raw_a"] += 1
                    if not ma["stop_geometry_ok"]:
                        counters["geo_a"] += 1
                mb = setup_b_metrics(hist, direction)
                b_core = bool(mb and mb["squeeze"] and mb["context_ok"])
                b_valid = b_core and mb["stop_geometry_ok"]
                if b_core:
                    counters["raw_b"] += 1
                    if not mb["stop_geometry_ok"]:
                        counters["geo_b"] += 1
                if a_valid or b_valid:
                    counters["signals"] += 1
                    if cand_dir == direction:
                        counters["rs_pass"] += 1
                        trig = ma["trigger"] if a_valid else mb["trigger"]
                        bar = df.iloc[i]
                        hit = (
                            bar["high"] >= trig if direction == "long" else bar["low"] <= trig
                        )
                        counters["filled" if hit else "unfilled"] += 1
                    else:
                        counters["rs_discard"] += 1

    c = counters
    print(f"\nSegnali grezzi (condizioni core, pre-geometria), barre-direzione dal {START.date()}:")
    print(f"  Setup A core ok : {c['raw_a']:5d}   scartati da geometria stop: {c['geo_a']}")
    print(f"  Setup B core ok : {c['raw_b']:5d}   scartati da geometria stop: {c['geo_b']}")
    print(f"  Segnali validi (post geometria)          : {c['signals']}")
    print(f"    scartati dal gate RS/trend dello screener: {c['rs_discard']} "
          f"({c['rs_discard']/max(c['signals'],1)*100:.0f}%)")
    print(f"    passati dal gate                          : {c['rs_pass']}")
    print(f"      di cui trigger rotto il giorno dopo     : {c['filled']}")
    print(f"      trigger non rotto (nessun trade)        : {c['unfilled']}")
    print("  (nota: sono barre-segnale, non trade: un trade consuma il segnale")
    print("   e blocca i successivi finché la posizione è aperta)")

    no_rs = run_variant(data, bench, signal_builder=build_trend_only_signal_builder())
    print("\nRerun con gate RS percentile DISATTIVATO (resta solo trend EMA50):")
    base = run_variant(data, bench)
    print(row("baseline (screener completo)", base))
    print(row("senza gate RS (solo trend EMA50)", no_rs))
    for dim in ("setup", "direction"):
        for k, a in aggregate_by(no_rs, dim).items():
            pf = a["profit_factor"]
            print(f"    {dim}={k}: n={a['n_trades']} WR={a['win_rate']*100:.0f}% "
                  f"exp={a['expectancy_r']:+.2f}R PF={pf if pf != float('inf') else 'inf'}")
    return no_rs


# ---------------------------------------------------------------------------
# Punto 6 — verifica costi
# ---------------------------------------------------------------------------


def point6(base: list[Trade]) -> None:
    sep("PUNTO 6 — Verifica costi su 5 trade campione")
    from engine.backtest import CRYPTO_FUNDING_DAILY, CRYPTO_TAKER_FEE

    for t in base[:5]:
        fee_in = CRYPTO_TAKER_FEE * t.size_units * t.entry
        fee_out = CRYPTO_TAKER_FEE * t.size_units * t.exit
        funding = CRYPTO_FUNDING_DAILY * t.size_units * t.entry * t.days_held
        total = fee_in + fee_out + funding
        cost_r_check = total / t.risk_amount if t.risk_amount else 0.0
        real_days = (t.exit_date - t.entry_date).total_seconds() / 86_400.0
        print(f"\n{t.entry_date.date()} {t.symbol} {t.setup} in={t.entry:.6g} out={t.exit:.6g} "
              f"size={t.size_units:.6f} risk={t.risk_amount:.2f}$")
        print(f"  fee entry  = {CRYPTO_TAKER_FEE}*size*entry = {fee_in:.4f}$")
        print(f"  fee exit   = {CRYPTO_TAKER_FEE}*size*exit  = {fee_out:.4f}$")
        print(f"  funding    = {CRYPTO_FUNDING_DAILY}/g * {t.days_held}g * notional = {funding:.4f}$")
        print(f"  totale     = {total:.4f}$  ->  in R: {cost_r_check:.4f}")
        print(f"  cost_r registrato dal simulatore: {t.cost_r:.4f}  "
              f"{'OK' if abs(cost_r_check - t.cost_r) < 5e-4 else 'MISMATCH!'}")
        print(f"  durata reale {real_days:.0f}g vs days_held {t.days_held}g  "
              f"{'OK' if abs(real_days - t.days_held) < 0.01 else 'MISMATCH!'}")
        print(f"  slippage: NON modellato per crypto (fill a trigger/open esatti)")


# ---------------------------------------------------------------------------
# Punto 7 — universo top 30
# ---------------------------------------------------------------------------


def _top_symbols_no_floor(n: int = 30) -> list[str]:
    """Top N per quote volume SENZA il floor di liquidità da 25M$ (solo diagnosi:
    oggi il floor riduce l'universo di produzione a ~12 simboli)."""
    from data.binance_client import LEVERAGED_SUFFIXES, SPOT, STABLECOINS, _get

    data = _get(f"{SPOT}/api/v3/ticker/24hr")
    rows = []
    for t in data:
        sym = t["symbol"]
        if not sym.endswith("USDT"):
            continue
        base = sym[:-4]
        if base in STABLECOINS or base.endswith(LEVERAGED_SUFFIXES):
            continue
        rows.append((sym, float(t.get("quoteVolume", 0))))
    rows.sort(key=lambda x: x[1], reverse=True)
    return [s for s, _ in rows[:n]]


def point7() -> None:
    sep("PUNTO 7 — Universo top-30 crypto dal 2022 (gate RS come in produzione)")
    prod_syms = binance_client.top_usdt_symbols(30)
    print(f"Universo di PRODUZIONE oggi (floor 25M$): {len(prod_syms)} simboli — "
          "troppo pochi per >150 trade.")
    print("Per la diagnosi uso i top 30 per volume SENZA floor di liquidità.")
    print("Costituenti ATTUALI: survivorship bias anche qui — i token delistati o")
    print("decaduti fuori dalla top 30 non sono nel campione.")
    syms = _top_symbols_no_floor(30)
    print(f"Simboli: {', '.join(syms)}")
    data, bench = load_data(syms)
    print(f"Simboli con storico sufficiente: {len(data)}")
    for sym, df in sorted(data.items()):
        print(f"  {sym:12s} {df.index[0].date()} -> {df.index[-1].date()} ({len(df)} barre)")

    print("\nPre-calcolo candidati screener per data...")
    cand_cache = build_candidate_cache(data, bench)
    builder = build_cached_signal_builder(cand_cache)
    trades = run_variant(data, bench, signal_builder=builder)
    trades_to_csv(trades, "backtest_trades_top30.csv")
    print(f"CSV scritto: backtest_trades_top30.csv ({len(trades)} trade)")

    is_t = [t for t in trades if t.entry_date < SPLIT]
    oos_t = [t for t in trades if t.entry_date >= SPLIT]
    print()
    print(row("TOTALE", trades))
    print(row(f"IN-SAMPLE (< {SPLIT.date()})", is_t))
    print(row(f"OUT-OF-SAMPLE (>= {SPLIT.date()})", oos_t))
    for dim in ("setup", "direction", "exit_reason"):
        print(f"\n  per {dim}:")
        for k, a in aggregate_by(trades, dim).items():
            pf = a["profit_factor"]
            print(f"    {k:14s} n={a['n_trades']:4d} WR={a['win_rate']*100:5.1f}% "
                  f"exp={a['expectancy_r']:+.3f}R PF={pf if pf != float('inf') else 'inf'}")
    amb = sum(1 for t in trades if t.exit_ambiguous)
    sb = sum(1 for t in trades if t.exit_reason == "stop_same_bar")
    losers = [t for t in trades if t.r_net <= 0]
    print(f"\n  barre di uscita ambigue: {amb}/{len(trades)}")
    print(f"  morti su entry-bar     : {sb}/{len(trades)}")
    if losers:
        print(f"  MFE mediana perdenti   : {statistics.median([t.mfe_r for t in losers]):+.2f}R")


def main() -> None:
    if "--top30-only" in sys.argv:
        point7()
        return
    print("Scarico BTCUSDT + ETHUSDT dal 2021-11 (warmup 400g)...")
    data, bench = load_data(["BTCUSDT", "ETHUSDT"])
    base = run_variant(data, bench)

    point1(base)
    point2(data, bench, base)
    point3(data, bench, base)
    point4(data, base)
    point5(data, bench)
    point6(base)
    if "--top30" in sys.argv:
        point7()


if __name__ == "__main__":
    main()
