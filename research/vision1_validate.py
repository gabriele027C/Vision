"""Validazione pre-registrata di VISION-1 — NESSUNA nuova variante.

Configurazione congelata (dichiarata PRIMA di vedere i dati di questa sessione):
  VISION-1 = Setup A/B
             + entry a chiusura daily oltre il trigger (confirm, fill a close)
             + stop Setup B = trigger +/- 1.5*ATR (bstop15)
             + uscita all-out a 2R
             + NIENTE gate RS (solo trend EMA50 per la direzione)
             + NIENTE filtro regime
             + NIENTE uscite parziali
             + RVOL registrato per trade (NON filtro hard)

Esecuzioni (ciascuna una sola volta):
  1. Crypto vergine  2019-01-01 -> 2021-12-31  (universo 23 simboli ablation)
  2. Stock vergine   2022-01-01 -> 2026-07-26  (S&P500+NDX100 + filtri liquidità live)
  3. Contaminato     crypto 2022-24 IS / 2025-26 OOS su VISION-1 (solo riferimento)
  4. Analisi RVOL post-hoc descrittiva sui trade di (1) e (2)

Criterio di successo (pre-registrato):
  candidata al forward su un mercato se, su quel dataset vergine:
    expectancy >= +0.05R  AND  n >= 60  AND  PF >= 1.05

CLI (dalla root del repo):
  python research/vision1_validate.py
"""
from __future__ import annotations

import pickle
import sys
from dataclasses import dataclass, field
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1] / "src" / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

import numpy as np
import pandas as pd
import yfinance as yf

from config import (
    MAX_STOP_ATR,
    STOCK_MIN_ADR_PCT,
    STOCK_MIN_AVG_VOLUME,
    STOCK_MIN_PRICE,
)
from data import binance_client, stocks_client
from engine.backtest import (
    CRYPTO_FUNDING_DAILY,
    CRYPTO_TAKER_FEE,
    MIN_BARS,
    STOCK_COMMISSION_PER_SHARE,
    STOCK_MIN_COMMISSION,
    STOCK_SLIPPAGE_PCT,
    wilson_ci,
)
from engine.indicators import adr_pct, atr as atr_fn, ema, rvol
from engine.setups import RANGE_BARS, _round_px, setup_a_metrics, setup_b_metrics
from engine.sizing import position_size

# --- Universo crypto fisso (identico ad ablation_study) ---
CRYPTO_UNIVERSE = [
    "AAVEUSDT", "BANKUSDT", "BNBUSDT", "BTCUSDT", "DEXEUSDT", "DOGEUSDT",
    "ENAUSDT", "ETHUSDT", "EULUSDT", "LINKUSDT", "LTCUSDT", "NEARUSDT",
    "ONDOUSDT", "PEPEUSDT", "PUMPUSDT", "SHIBUSDT", "SOLUSDT", "SUIUSDT",
    "TRXUSDT", "VANAUSDT", "WLDUSDT", "XRPUSDT", "ZECUSDT",
]

DATA_END = pd.Timestamp("2026-07-26", tz="UTC")
CAPITAL, RISK_PCT = 10_000.0, 1.0
CACHE = Path(__file__).parent / "diag_cache" / "vision1"
CACHE.mkdir(parents=True, exist_ok=True)

# Criterio di successo pre-registrato
MIN_N, MIN_EXP, MIN_PF = 60, 0.05, 1.05

# Conteggio configurazioni esplorate PRIMA di questa validazione (non include VISION-1
# validation runs: non sono varianti, sono esecuzioni della config congelata).
# Ablation report: 51; diagnostica precedente (~10: default/market 2-sym, ambiguità,
# entry-bar, rs-off, top30, random sanity, ecc.).
N_CONFIGS_EXPLORED = 51 + 10  # ~61; vedi report per dettaglio


# ---------------------------------------------------------------------------
# VISION-1: simulatore congelato (confirm + bstop15 + rs-off + allout)
# ---------------------------------------------------------------------------


@dataclass
class TradeRec:
    symbol: str
    setup: str
    direction: str
    signal_date: pd.Timestamp
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry: float
    stop0: float
    r_net: float
    reason: str
    rvol: float
    market: str
    legs: list = field(default_factory=list)


def _bstop15(b: dict, direction: str) -> tuple[float, float] | None:
    """Stop Setup B = trigger +/- 1.5*ATR (VISION-1)."""
    a = b["atr"]
    trig = float(b["trigger"])
    stop = (trig - 1.5 * a) if direction == "long" else (trig + 1.5 * a)
    if abs(trig - stop) > MAX_STOP_ATR * a or abs(trig - stop) <= 0:
        return None
    return _round_px(trig), _round_px(stop)


def _costs(market: str, entry: float, exit_px: float, size: float, days: float) -> float:
    if market == "crypto":
        return (
            CRYPTO_TAKER_FEE * size * (entry + exit_px)
            + CRYPTO_FUNDING_DAILY * size * entry * max(days, 0.0)
        )
    commission = 2 * max(STOCK_COMMISSION_PER_SHARE * size, STOCK_MIN_COMMISSION)
    slippage = STOCK_SLIPPAGE_PCT * size * (entry + exit_px)
    return commission + slippage


def _finish(pos: dict, legs: list, market: str) -> TradeRec:
    entry, runit, sign = pos["entry"], pos["runit"], pos["sign"]
    r_gross = sum(frac * sign * (px - entry) / runit for frac, px, _, _ in legs)
    cost = 0.0
    for frac, px, dt, _ in legs:
        days = max((dt - pos["entry_date"]).total_seconds() / 86_400.0, 0.0)
        cost += _costs(market, entry, px, frac * pos["size"], days)
    r_net = r_gross - cost / pos["risk_amt"]
    return TradeRec(
        symbol=pos["symbol"], setup=pos["setup"], direction=pos["dir"],
        signal_date=pos["signal_date"], entry_date=pos["entry_date"],
        exit_date=legs[-1][2], entry=entry, stop0=pos["stop0"],
        r_net=round(r_net, 4), reason="+".join(r for _, _, _, r in legs),
        rvol=pos["rvol"], market=market, legs=legs,
    )


def _step_exit_allout(pos, legs, i, o, h, low, c, idx) -> bool:
    """All-out a 2R / stop — ordine pessimistico (stop prima del target)."""
    sign = pos["sign"]
    date = idx[i]
    oi, hi, li = float(o[i]), float(h[i]), float(low[i])
    hi_fav = hi if sign > 0 else li
    lo_adv = li if sign > 0 else hi

    def hit_below(level):
        return sign * (level - lo_adv) >= 0

    def hit_above(level):
        return sign * (hi_fav - level) >= 0

    def gap_below(level):
        return sign * (level - oi) >= 0

    def gap_above(level):
        return sign * (oi - level) >= 0

    if gap_below(pos["stop"]):
        legs.append((1.0, oi, date, "stop_gap")); return True
    if hit_below(pos["stop"]):
        legs.append((1.0, pos["stop"], date, "stop")); return True
    if gap_above(pos["tgt"]):
        legs.append((1.0, oi, date, "target_gap")); return True
    if hit_above(pos["tgt"]):
        legs.append((1.0, pos["tgt"], date, "target")); return True
    return False


def simulate_vision1(
    data: dict[str, pd.DataFrame],
    table: dict,
    *,
    market: str,
    start: pd.Timestamp,
    end: pd.Timestamp | None = None,
) -> list[TradeRec]:
    """VISION-1 congelata: confirm + bstop15 + rs-off + allout. Una sola logica."""
    trades: list[TradeRec] = []
    for sym, df in data.items():
        idx = df.index
        o = df["open"].to_numpy()
        h = df["high"].to_numpy()
        low = df["low"].to_numpy()
        c = df["close"].to_numpy()
        pos: dict | None = None
        legs: list = []

        for i in range(MIN_BARS, len(df)):
            date = idx[i]

            if pos is not None:
                if _step_exit_allout(pos, legs, i, o, h, low, c, idx):
                    trades.append(_finish(pos, legs, market))
                    pos, legs = None, []
                continue

            # Nuove entry solo dentro [start, end]
            if end is not None and date > end:
                break
            if date < start:
                continue
            info = table.get((sym, idx[i - 1]))
            if info is None:
                continue
            direction = info["trend"]  # rs-off: solo EMA50

            if info["a"] is not None:
                setup, trig, stop = "A", info["a"]["trigger"], info["a"]["stop"]
            elif info["b"] is not None:
                levels = _bstop15(info["b"], direction)
                if levels is None:
                    continue
                setup, (trig, stop) = "B", levels
            else:
                continue

            sign = 1.0 if direction == "long" else -1.0
            # CONFIRM proxy: daily deve CHIUDERE oltre il trigger; fill a close
            if not (sign * (float(c[i]) - trig) > 0):
                continue
            fill = float(c[i])

            runit = sign * (fill - stop)
            if runit <= 0:
                continue
            sizing = position_size(
                CAPITAL, RISK_PCT, fill, stop, direction=direction, market=market
            )
            if "error" in sizing:
                continue
            pos = {
                "symbol": sym, "setup": setup, "dir": direction, "sign": sign,
                "signal_date": idx[i - 1], "entry_date": date, "entry": fill,
                "stop": stop, "stop0": stop, "runit": runit,
                "tgt": fill + sign * 2 * runit,
                "size": float(sizing["size_units"]),
                "risk_amt": float(sizing["risk_amount"]),
                "rvol": info["rvol"],
            }
            legs = []
            # confirm: niente stop sulla barra di entry (fill a close)

        # Posizione ancora aperta a fine dati: scartata (come il backtester).
        # Non forziamo eof: eviterebbe di contare un'uscita inventata.

    trades.sort(key=lambda t: t.entry_date)
    return trades


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------


def _ensure_utc(df: pd.DataFrame) -> pd.DataFrame:
    if df.index.tz is None:
        df = df.copy()
        df.index = df.index.tz_localize("UTC")
    else:
        df = df.copy()
        df.index = df.index.tz_convert("UTC")
    return df


def load_crypto(
    symbols: list[str],
    start: pd.Timestamp,
    end: pd.Timestamp,
    tag: str,
) -> tuple[dict[str, pd.DataFrame], list[str]]:
    """Scarica daily crypto. Esclude solo chi non ha abbastanza barre
    TRADEABILI nel periodo (warmup MIN_BARS prima di una entry in [start,end])."""
    warmup_ms = int((start - pd.Timedelta(days=400)).timestamp() * 1000)
    data: dict[str, pd.DataFrame] = {}
    excluded: list[str] = []
    for sym in symbols:
        f = CACHE / f"crypto_{tag}_{sym}.pkl"
        if f.exists():
            df = pd.read_pickle(f)
        else:
            try:
                df = binance_client.klines_range(sym, "1d", warmup_ms).iloc[:-1]
            except Exception as exc:
                print(f"  {sym}: download fallito ({exc}) — escluso")
                excluded.append(sym)
                continue
            df.to_pickle(f)
        df = _ensure_utc(df)
        df = df.loc[df.index <= end]
        # Entry possibili: barre i>=MIN_BARS con date in [start, end]
        n_tradeable = 0
        for i in range(MIN_BARS, len(df)):
            if start <= df.index[i] <= end:
                n_tradeable += 1
        if n_tradeable < 20:
            excluded.append(sym)
            continue
        data[sym] = df
    return data, excluded


def _signals_for_symbol(sym: str, df: pd.DataFrame, min_sig: pd.Timestamp) -> dict:
    """Worker per-simbolo (parallelizzabile): stessa logica di build_signal_table."""
    out: dict = {}
    close = df["close"]
    e50 = ema(close, 50)
    rv = rvol(df["volume"])
    for i in range(MIN_BARS, len(df)):
        d = df.index[i - 1]
        if d < min_sig:
            continue
        hist = df.iloc[:i]
        trend = "long" if float(close.iloc[i - 1]) > float(e50.iloc[i - 1]) else "short"
        ma = setup_a_metrics(hist, trend)
        a = None
        if ma and ma["aligned"] and ma["in_zone"] and ma["momentum_ok"] \
                and ma["vol_declining"] and ma["stop_geometry_ok"]:
            a = {"trigger": _round_px(ma["trigger"]), "stop": _round_px(ma["stop"])}
        mb = setup_b_metrics(hist, trend)
        b = None
        if mb and mb["squeeze"] and mb["context_ok"]:
            b = {
                "trigger": _round_px(mb["trigger"]),
                "stop": _round_px(mb["stop"]),
                "atr": float(mb["atr"]),
                "rng_high": float(df["high"].iloc[i - RANGE_BARS - 1:i - 1].max()),
                "rng_low": float(df["low"].iloc[i - RANGE_BARS - 1:i - 1].min()),
            }
        if a is None and b is None:
            continue
        out[(sym, d)] = {
            "trend": trend,
            "rvol": float(rv.iloc[i - 1]) if pd.notna(rv.iloc[i - 1]) else 0.0,
            "a": a,
            "b": b,
        }
    return out


def build_signal_table(data: dict[str, pd.DataFrame], start: pd.Timestamp) -> dict:
    """Segnali VISION-1: trend EMA50, Setup A/B (default params), RVOL. No RS, no regime."""
    import os
    from concurrent.futures import ProcessPoolExecutor, as_completed

    min_sig = start - pd.Timedelta(days=2)
    table: dict = {}
    items = list(data.items())
    n_workers = min(8, max(1, (os.cpu_count() or 4) - 1))

    if len(items) <= 6:
        for i, (sym, df) in enumerate(items, 1):
            table.update(_signals_for_symbol(sym, df, min_sig))
            print(f"    segnali {i}/{len(items)}...", flush=True)
        return table

    print(f"    ProcessPool {n_workers} worker x {len(items)} simboli...", flush=True)
    done = 0
    with ProcessPoolExecutor(max_workers=n_workers) as ex:
        futs = [ex.submit(_signals_for_symbol, sym, df, min_sig) for sym, df in items]
        for fut in as_completed(futs):
            table.update(fut.result())
            done += 1
            if done % 20 == 0 or done == len(items):
                print(f"    segnali {done}/{len(items)}...", flush=True)
    return table


def load_stocks(start: pd.Timestamp, end: pd.Timestamp) -> tuple[dict[str, pd.DataFrame], dict]:
    """Universo S&P500+NDX100 + filtri liquidita live (prezzo/vol/ADR sull'ultima barra)."""
    import json

    meta = {"universe_raw": 0, "after_liq": 0, "with_history": 0}
    f_uni = CACHE / "stock_universe.json"
    if f_uni.exists():
        symbols = json.loads(f_uni.read_text())
    else:
        symbols = stocks_client.stock_universe()
        f_uni.write_text(json.dumps(symbols))
    meta["universe_raw"] = len(symbols)
    print(f"  Universo grezzo S&P500+NDX100: {len(symbols)} simboli")

    dl_start = (start - pd.Timedelta(days=450)).strftime("%Y-%m-%d")
    f_data = CACHE / "stocks_ohlcv.pkl"
    if f_data.exists():
        raw: dict[str, pd.DataFrame] = pickle.loads(f_data.read_bytes())
        print(f"  Cache stock: {len(raw)} ticker")
    else:
        print(f"  Download Yahoo {dl_start} -> {end.date()} ...")
        raw = {}
        chunk_size = 80
        for i in range(0, len(symbols), chunk_size):
            chunk = symbols[i:i + chunk_size]
            print(f"    chunk {i // chunk_size + 1}/{(len(symbols) + chunk_size - 1) // chunk_size} "
                  f"({len(chunk)} ticker)...")
            data = yf.download(
                chunk, start=dl_start, end=(end + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                interval="1d", group_by="ticker", auto_adjust=True,
                threads=True, progress=False,
            )
            if data is None or data.empty:
                continue
            for tkr in chunk:
                try:
                    df = data[tkr] if len(chunk) > 1 else data
                except KeyError:
                    continue
                if df is None or df.empty:
                    continue
                df = df.dropna(subset=["Close"])
                if len(df) < MIN_BARS:
                    continue
                df = df.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]]
                df = _ensure_utc(df)
                raw[tkr] = df
        f_data.write_bytes(pickle.dumps(raw))
        print(f"  Scaricati {len(raw)} ticker con storico")

    filtered: dict[str, pd.DataFrame] = {}
    for sym, df in raw.items():
        df = df.loc[df.index <= end]
        if len(df) < MIN_BARS:
            continue
        last = float(df["close"].iloc[-1])
        avg_vol = float(df["volume"].rolling(20).mean().iloc[-1])
        if last < STOCK_MIN_PRICE or avg_vol < STOCK_MIN_AVG_VOLUME:
            continue
        if adr_pct(df) < STOCK_MIN_ADR_PCT:
            continue
        pre = df.loc[df.index < start]
        if len(pre) < MIN_BARS:
            continue
        filtered[sym] = df
    meta["after_liq"] = len(filtered)
    meta["with_history"] = len(filtered)
    return filtered, meta


# ---------------------------------------------------------------------------
# Metriche / report
# ---------------------------------------------------------------------------


def agg(trades: list[TradeRec]) -> dict:
    n = len(trades)
    if n == 0:
        return {"n": 0}
    rs = [t.r_net for t in trades]
    wins = sum(1 for r in rs if r > 0)
    lo, hi = wilson_ci(wins, n)
    gw = sum(r for r in rs if r > 0)
    gl = -sum(r for r in rs if r < 0)
    eq = peak = dd = 0.0
    for r in rs:
        eq += r
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
    return {
        "n": n, "wr": wins / n, "ci": (lo, hi),
        "exp": sum(rs) / n,
        "pf": (gw / gl) if gl > 0 else float("inf"),
        "dd": dd, "tot": sum(rs),
    }


def fmt(label: str, trades: list[TradeRec]) -> str:
    a = agg(trades)
    if a["n"] == 0:
        return f"{label:36s} n=   0  —"
    lo, hi = a["ci"]
    pf = f"{a['pf']:.2f}" if a["pf"] != float("inf") else "inf"
    return (f"{label:36s} n={a['n']:4d}  WR={a['wr']*100:5.1f}% "
            f"(CI {lo*100:.0f}-{hi*100:.0f}%)  exp={a['exp']:+.3f}R  "
            f"PF={pf}  DD={a['dd']:.1f}R")


def print_breakdown(trades: list[TradeRec]) -> None:
    print(fmt("  TOTALE", trades))
    for v in ("A", "B"):
        print(fmt(f"  setup={v}", [t for t in trades if t.setup == v]))
    for v in ("long", "short"):
        print(fmt(f"  direction={v}", [t for t in trades if t.direction == v]))


def rvol_buckets(trades: list[TradeRec], title: str) -> None:
    print(f"\n  {title}")
    edges = [
        ("RVOL < 1.0", lambda r: r < 1.0),
        ("RVOL 1.0-1.5", lambda r: 1.0 <= r < 1.5),
        ("RVOL 1.5-2.0", lambda r: 1.5 <= r < 2.0),
        ("RVOL > 2.0", lambda r: r >= 2.0),
    ]
    for label, pred in edges:
        sub = [t for t in trades if pred(t.rvol)]
        print("   ", fmt(label, sub))


def passes(trades: list[TradeRec]) -> bool:
    a = agg(trades)
    if a["n"] < MIN_N:
        return False
    if a["exp"] < MIN_EXP:
        return False
    pf = a["pf"] if a["pf"] != float("inf") else 999.0
    return pf >= MIN_PF


def run_period(
    label: str,
    data: dict[str, pd.DataFrame],
    market: str,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> list[TradeRec]:
    print(f"\nPrecompute segnali VISION-1 ({label}, {len(data)} simboli)...")
    sig_cache = CACHE / f"signals_{label}.pkl"
    if sig_cache.exists():
        print(f"  cache segnali: {sig_cache.name}")
        table = pickle.loads(sig_cache.read_bytes())
    else:
        table = build_signal_table(data, start)
        sig_cache.write_bytes(pickle.dumps(table))
        print(f"  segnali salvati: {len(table)} barre-segnale")
    trades = simulate_vision1(data, table, market=market, start=start, end=end)
    trades = [t for t in trades if t.entry_date <= end]
    return trades


# ---------------------------------------------------------------------------
# Main — una sola passata, nessun ritocco
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 78)
    print("VISION-1 — VALIDAZIONE PRE-REGISTRATA (nessuna nuova variante)")
    print("=" * 78)
    print("Config: confirm(fill@close) + bstop15 + allout@2R + rs-off + no-regime")
    print("         RVOL registrato, NON filtro hard")
    print(f"Criterio successo: exp>={MIN_EXP:+.2f}R  n>={MIN_N}  PF>={MIN_PF}")
    print(f"Configurazioni esplorate prima del freeze: ~{N_CONFIGS_EXPLORED}")

    # ----- 1. Crypto vergine 2019-2021 -----
    print("\n" + "=" * 78)
    print("1. CRYPTO VERGINE  2019-01-01 -> 2021-12-31")
    print("=" * 78)
    c_start = pd.Timestamp("2019-01-01", tz="UTC")
    c_end = pd.Timestamp("2021-12-31", tz="UTC")
    print("Scarico/carico universo 23 simboli...")
    crypto_v, excluded = load_crypto(CRYPTO_UNIVERSE, c_start, c_end, tag="v2019")
    print(f"Simboli USATI ({len(crypto_v)}): {', '.join(sorted(crypto_v))}")
    print(f"Simboli ESCLUSI per mancanza storico ({len(excluded)}): "
          f"{', '.join(excluded) if excluded else 'nessuno'}")
    print("AVVERTENZA: escludere i simboli senza storico 2019-21 PEGGIORA il")
    print("survivorship bias (restano i sopravvissuti liquidi di allora-e-oggi).")
    trades_cv = run_period("crypto-vergine", crypto_v, "crypto", c_start, c_end)
    print_breakdown(trades_cv)
    ok_crypto = passes(trades_cv)
    print(f"\n  Criterio successo crypto vergine: "
          f"{'PASS' if ok_crypto else 'FAIL'}")

    # ----- 2. Stock vergine 2022-2026 -----
    print("\n" + "=" * 78)
    print("2. STOCK VERGINE  2022-01-01 -> 2026-07-26")
    print("=" * 78)
    print("AVVERTENZA SURVIVORSHIP: costituenti ATTUALI S&P500+Nasdaq100;")
    print("i titoli rimossi dagli indici (spesso i peggiori) non sono nel campione.")
    s_start = pd.Timestamp("2022-01-01", tz="UTC")
    s_end = DATA_END
    stocks, meta = load_stocks(s_start, s_end)
    print(f"  Dopo filtri liquidità (price>={STOCK_MIN_PRICE}, "
          f"avgVol>={STOCK_MIN_AVG_VOLUME}, ADR>={STOCK_MIN_ADR_PCT}%): "
          f"{meta['after_liq']} simboli")
    trades_sv = run_period("stock-vergine", stocks, "stocks", s_start, s_end)
    print_breakdown(trades_sv)
    ok_stock = passes(trades_sv)
    print(f"\n  Criterio successo stock vergine: "
          f"{'PASS' if ok_stock else 'FAIL'}")

    # ----- 3. Contaminato crypto IS/OOS su VISION-1 (solo riferimento) -----
    print("\n" + "=" * 78)
    print("3. CRYPTO CONTAMINATO (VISION-1 su 2022-26) — LETTURA GIÀ VISTA, NON VERGINE")
    print("=" * 78)
    print("Dichiarato contaminato: lo stesso universo/periodo è stato usato in")
    print("ablazione. I numeri servono SOLO come riga di riferimento nella tabella.")
    t_start = pd.Timestamp("2022-01-01", tz="UTC")
    split = pd.Timestamp("2025-01-01", tz="UTC")
    crypto_c, excl2 = load_crypto(CRYPTO_UNIVERSE, t_start, DATA_END, tag="c2022")
    # riusa gli stessi 23 se disponibili; esclusioni tipicamente poche
    if excl2:
        print(f"  Esclusi su 2022-26: {', '.join(excl2)}")
    trades_all = run_period("crypto-contaminato", crypto_c, "crypto", t_start, DATA_END)
    trades_is = [t for t in trades_all if t.entry_date < split]
    trades_oos = [t for t in trades_all if t.entry_date >= split]
    print("\n  --- IS 2022-24 (contaminato) ---")
    print_breakdown(trades_is)
    print("\n  --- OOS 2025-26 (contaminato) ---")
    print_breakdown(trades_oos)

    # ----- 4. RVOL post-hoc -----
    print("\n" + "=" * 78)
    print("4. ANALISI RVOL POST-HOC (descrittiva — NON modifica VISION-1)")
    print("=" * 78)
    rvol_buckets(trades_cv, "Crypto vergine 2019-21")
    rvol_buckets(trades_sv, "Stock vergine 2022-26")

    # ----- Report finale -----
    print("\n" + "=" * 78)
    print("REPORT FINALE — TABELLA UNICA VISION-1")
    print("=" * 78)

    def row(name: str, tr: list[TradeRec], note: str = "") -> None:
        a = agg(tr)
        if a["n"] == 0:
            print(f"{name:32s} n=   0  —  {note}")
            return
        lo, hi = a["ci"]
        pf = f"{a['pf']:.2f}" if a["pf"] != float("inf") else "inf"
        flag = ""
        if "vergine" in name.lower():
            flag = " PASS" if passes(tr) else " FAIL"
        print(f"{name:32s} n={a['n']:4d}  WR={a['wr']*100:5.1f}% "
              f"(CI {lo*100:.0f}-{hi*100:.0f}%)  exp={a['exp']:+.3f}R  "
              f"PF={pf}  DD={a['dd']:.1f}R{flag}  {note}")

    row("IS crypto 2022-24 (contam.)", trades_is, "[contaminato]")
    row("OOS crypto 2025-26 (contam.)", trades_oos, "[contaminato]")
    row("Crypto vergine 2019-21", trades_cv, "")
    row("Stock vergine 2022-26", trades_sv, "")

    print("\n--- VERDETTO (criterio pre-registrato) ---")
    if ok_crypto and ok_stock:
        print("VISION-1 candidata al forward test su ENTRAMBI i mercati.")
    elif ok_crypto:
        print("VISION-1 candidata al forward test SOLO su CRYPTO.")
        print("Su stock l'edge non supera la soglia pre-registrata.")
    elif ok_stock:
        print("VISION-1 candidata al forward test SOLO su STOCK.")
        print("Su crypto l'edge non supera la soglia pre-registrata.")
    else:
        print("FALLIMENTO SU ENTRAMBI I DATASET VERGINI.")
        print("L'edge residuo di VISION-1 non è distinguibile da zero.")
        print("Nessuna attenuante: la configurazione NON è candidata al forward.")

    print(f"\nConfigurazioni testate nell'intero progetto ad oggi (esplorazione): "
          f"~{N_CONFIGS_EXPLORED}")
    print("Questa sessione: 0 nuove varianti; solo esecuzioni della config congelata.")
    print("\nAVVERTENZA SURVIVORSHIP:")
    print("  Crypto: costituenti attuali top-30; sul 2019-21 i simboli senza storico")
    print(f"  sono esclusi ({len(excluded)}): {', '.join(excluded) if excluded else 'n/d'}")
    print("  -> campione ancora più selezionato verso i sopravvissuti.")
    print("  Stock: costituenti ATTUALI S&P500+Nasdaq100 + filtri liquidità odierni;")
    print("  i delistati/rimossi non compaiono -> risultati ottimistici.")
    print("\nIpotesi future (ANNOTATE, non testate ora):")
    print("  - eventuale filtro RVOL hard se i bucket post-hoc lo suggeriscono")
    print("  - conferma 4H reale al posto del proxy close-beyond-trigger")
    print("  - qualsiasi modifica a VISION-1 richiede una NUOVA pre-registrazione")


if __name__ == "__main__":
    # Force unbuffered-ish line output
    sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, "reconfigure") else None
    main()
