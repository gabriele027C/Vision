"""Studio di ablazione sul backtest — filtri, geometria Setup B, gestione uscite.

NON modifica il motore live (setups.py, screener.py, scanner.py): tutte le
varianti sono parametri di questo script, che riusa le funzioni del motore in
sola lettura. Universo FISSO (i 23 simboli del run a 208 trade), dati congelati
al 2026-07-26 (cache su disco in diag_cache/), costi identici al backtester.

Regola vincolante rispettata: le PARTI 1-3 stampano SOLO risultati IN-SAMPLE
(entry < 2025-01-01); l'out-of-sample viene stampato UNA volta sola dalla
PARTE 4 sulla configurazione scelta.

CLI (dalla root del repo; ogni numero del report è rieseguibile):
  python research/ablation_study.py list
  python research/ablation_study.py part1|part2|part3|part4|all
  python research/ablation_study.py run NOME...
  python research/ablation_study.py rebuild-cache

Definizioni delle varianti (documentazione dei flag):
  base        pipeline identica al run a 208 trade: gate RS percentile+trend
              EMA50 (classify_candidates), Setup A poi B, entry al trigger,
              stop valutato anche sulla barra di entry, all-out a 2R.
  regime      + filtro regime: crypto_regime(BTC storia fino alla barra-segnale);
              long solo con mode=="long", short solo con mode=="short",
              nessun trade in "mixed" (il "neutral" della strategia).
  confirm     + conferma 4H (PROXY documentato: i dati 4H storici Binance non
              coprono tutto il periodo in modo affidabile per 23 simboli, quindi
              l'entry è valida solo se la barra daily successiva CHIUDE oltre il
              trigger; il fill avviene alla CHIUSURA di quella barra, non al
              trigger: regola eseguibile in reale, nessuna uscita same-bar).
  rs-cond     gate RS condizionato: attivo solo con universo >=10 simboli.
              Con questo universo (23) il gate resta attivo -> identico a base.
  rs-off      (informativo) gate RS spento, resta solo il trend EMA50: serve a
              misurare il contributo marginale del gate RS.
  rvol        + filtro RVOL hard: segnale valido solo con RVOL >= 1.5 (config
              RVOL_INTEREST) alla barra-segnale.
  bstop15     Setup B: stop = trigger -/+ 1.5*ATR (invece di max(trigger-ATR,
              rng_low)); la distanza è 1.5*ATR per costruzione, entro
              MAX_STOP_ATR=2.5. Target sempre 2R sul nuovo stop.
  bbuf        Setup B: trigger con buffer = rng_high + 0.25*ATR (long) /
              rng_low - 0.25*ATR (short); stop ricalcolato con la formula
              originale sul nuovo trigger.
  bgeo-both   bstop15 + bbuf insieme.
  exit-be     TP 50% a 1R, stop a breakeven sul resto, target 2R.
  exit-trail  TP 50% a 1R, trailing 1*ATR sul resto (chandelier dai massimi
              post-TP1), chiusura sotto EMA20 come uscita alternativa.
  Le combinazioni si scrivono unendo i nomi con "+", es.:
  python ablation_study.py run regime+confirm bstop15+exit-be

Scelte pessimistiche documentate (coerenti col backtester):
  - barra che tocca stop e target/TP1: vince lo stop;
  - sulla barra che filla il trigger si valuta solo lo stop (mai TP);
  - nel giorno del TP1, se il low tocca anche il nuovo stop (BE), il resto
    chiude a BE; il target non viene mai preso nella stessa barra del TP1;
  - posizioni aperte a fine dati: scartate se nessuna quota realizzata
    (come il backtester); chiuse all'ultimo close ("eof") se il TP1 era
    già stato incassato, per contabilizzare la quota realizzata.
"""
from __future__ import annotations

import pickle
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1] / "src" / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

import numpy as np
import pandas as pd

from data import binance_client
from engine.backtest import (
    CRYPTO_FUNDING_DAILY,
    CRYPTO_TAKER_FEE,
    MIN_BARS,
    wilson_ci,
)
from engine.indicators import atr as atr_fn
from engine.indicators import ema, rvol
from engine.screener import classify_candidates, rs_scores
from engine.setups import RANGE_BARS, _round_px, setup_a_metrics, setup_b_metrics
from engine.sizing import position_size
from config import MAX_STOP_ATR, RVOL_INTEREST

UNIVERSE = [
    "AAVEUSDT", "BANKUSDT", "BNBUSDT", "BTCUSDT", "DEXEUSDT", "DOGEUSDT",
    "ENAUSDT", "ETHUSDT", "EULUSDT", "LINKUSDT", "LTCUSDT", "NEARUSDT",
    "ONDOUSDT", "PEPEUSDT", "PUMPUSDT", "SHIBUSDT", "SOLUSDT", "SUIUSDT",
    "TRXUSDT", "VANAUSDT", "WLDUSDT", "XRPUSDT", "ZECUSDT",
]
START = pd.Timestamp("2022-01-01", tz="UTC")
SPLIT = pd.Timestamp("2025-01-01", tz="UTC")
DATA_END = pd.Timestamp("2026-07-26", tz="UTC")  # dataset congelato (riproducibile)
WARMUP_MS = int((START - pd.Timedelta(days=400)).timestamp() * 1000)
CAPITAL, RISK_PCT = 10_000.0, 1.0
RS_MIN_UNIVERSE = 10  # gate RS condizionato: attivo solo con universo >= 10

CACHE = Path(__file__).parent / "diag_cache"
CACHE.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Dati (congelati su disco) e precompute segnali
# ---------------------------------------------------------------------------


def load_data() -> dict[str, pd.DataFrame]:
    data: dict[str, pd.DataFrame] = {}
    for sym in UNIVERSE:
        f = CACHE / f"{sym}.pkl"
        if f.exists():
            df = pd.read_pickle(f)
        else:
            df = binance_client.klines_range(sym, "1d", WARMUP_MS).iloc[:-1]
            df.to_pickle(f)
        df = df.loc[df.index <= DATA_END]
        if len(df) > MIN_BARS:
            data[sym] = df
    return data


def build_regime_series(btc: pd.DataFrame) -> pd.Series:
    """crypto_regime vettorizzato: identico bar-per-bar (EMA con prefix property)."""
    close = btc["close"]
    e50, e200 = ema(close, 50), ema(close, 200)
    mode = pd.Series("mixed", index=btc.index)
    mode[(close > e200) & (close > e50)] = "long"
    mode[(close < e200) & (close < e50)] = "short"
    return mode


def build_candidate_cache(data: dict[str, pd.DataFrame], bench: pd.DataFrame) -> dict:
    """Direzione candidata RS per (data-barra-segnale) -> {sym: direction}.

    Stessa semantica di build_production_signal_fn: slice con index <= barra
    segnale (equivale a index < data di entry)."""
    f = CACHE / "abl_cands.pkl"
    if f.exists():
        return pickle.loads(f.read_bytes())
    dates = sorted({d for df in data.values() for d in df.index
                    if d >= START - pd.Timedelta(days=2)})
    cache: dict = {}
    for d in dates:
        slices = {s: df.loc[df.index <= d] for s, df in data.items()}
        slices = {s: df for s, df in slices.items() if len(df) >= MIN_BARS}
        bench_slice = bench.loc[bench.index <= d]
        if not slices or len(bench_slice) < MIN_BARS:
            cache[d] = {}
            continue
        scores = rs_scores(slices, bench_slice)
        cands = classify_candidates(slices, scores, True, True)
        cache[d] = {c["symbol"]: c["direction"] for c in cands}
    f.write_bytes(pickle.dumps(cache))
    return cache


def build_signal_table(data: dict[str, pd.DataFrame], bench: pd.DataFrame) -> dict:
    """Per (sym, data-barra-segnale): trend, candidato RS, regime, RVOL,
    Setup A valido (livelli), metriche core Setup B (per le varianti geometria).

    Riusa setup_a_metrics/setup_b_metrics del motore live in sola lettura."""
    f = CACHE / "abl_signals.pkl"
    if f.exists():
        return pickle.loads(f.read_bytes())
    cands = build_candidate_cache(data, bench)
    regime = build_regime_series(bench)
    table: dict = {}
    for sym, df in data.items():
        close = df["close"]
        e50 = ema(close, 50)
        rv = rvol(df["volume"])
        min_start = START - pd.Timedelta(days=2)
        for i in range(MIN_BARS, len(df)):
            d = df.index[i - 1]  # barra-segnale (l'entry avviene alla barra i)
            if d < min_start:
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
                    "geo_ok": bool(mb["stop_geometry_ok"]),
                    "trigger": _round_px(mb["trigger"]),
                    "stop": _round_px(mb["stop"]),
                    # Stesso range di setup_b_metrics (RANGE_BARS barre PRIMA della segnale)
                    "rng_high": float(df["high"].iloc[i - RANGE_BARS - 1:i - 1].max()),
                    "rng_low": float(df["low"].iloc[i - RANGE_BARS - 1:i - 1].min()),
                    "atr": float(mb["atr"]),
                }
            if a is None and b is None:
                continue
            table[(sym, d)] = {
                "trend": trend,
                "cand": cands.get(d, {}).get(sym),
                "regime": str(regime.get(d, "mixed")),
                "rvol": float(rv.iloc[i - 1]) if pd.notna(rv.iloc[i - 1]) else 0.0,
                "a": a,
                "b": b,
            }
    f.write_bytes(pickle.dumps(table))
    return table


# ---------------------------------------------------------------------------
# Configurazione varianti
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Config:
    name: str
    f_regime: bool = False
    f_confirm: bool = False
    rs_mode: str = "on"          # on | off | cond (cond==on con universo >=10)
    f_rvol: bool = False
    b_geo: str = "base"          # base | stop15 | buf | both
    exit_mode: str = "allout"    # allout | be | trail


ATOMS: dict[str, dict] = {
    "base": {},
    "regime": {"f_regime": True},
    "confirm": {"f_confirm": True},
    "rs-cond": {"rs_mode": "cond"},
    "rs-off": {"rs_mode": "off"},
    "rvol": {"f_rvol": True},
    "bstop15": {"b_geo": "stop15"},
    "bbuf": {"b_geo": "buf"},
    "bgeo-both": {"b_geo": "both"},
    "exit-be": {"exit_mode": "be"},
    "exit-trail": {"exit_mode": "trail"},
}


def make_config(name: str) -> Config:
    """'regime+confirm+bstop15' -> Config combinata."""
    kw: dict = {}
    for part in name.split("+"):
        if part not in ATOMS:
            raise SystemExit(f"variante sconosciuta: {part!r} (usa 'list')")
        for k, v in ATOMS[part].items():
            if k in kw and kw[k] != v:
                raise SystemExit(f"conflitto in {name!r} sul parametro {k}")
            kw[k] = v
    return Config(name=name, **kw)


# ---------------------------------------------------------------------------
# Simulatore con partial exit (stessi costi/fill del backtester)
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
    legs: list = field(default_factory=list)


def _leg_costs(entry: float, legs: list, size: float, entry_date) -> float:
    """fee taker su entrambe le gambe + funding pro-quota fino all'uscita di ogni gamba."""
    total = 0.0
    for frac, px, dt, _ in legs:
        days = max((dt - entry_date).total_seconds() / 86_400.0, 0.0)
        total += CRYPTO_TAKER_FEE * frac * size * (entry + px)
        total += CRYPTO_FUNDING_DAILY * frac * size * entry * days
    return total


def _finish(pos: dict, market_legs: list) -> TradeRec:
    entry, runit, sign = pos["entry"], pos["runit"], pos["sign"]
    r_gross = sum(frac * sign * (px - entry) / runit for frac, px, _, _ in market_legs)
    cost = _leg_costs(entry, market_legs, pos["size"], pos["entry_date"])
    r_net = r_gross - cost / pos["risk_amt"]
    reason = "+".join(r for _, _, _, r in market_legs)
    return TradeRec(
        symbol=pos["symbol"], setup=pos["setup"], direction=pos["dir"],
        signal_date=pos["signal_date"], entry_date=pos["entry_date"],
        exit_date=market_legs[-1][2], entry=entry, stop0=pos["stop0"],
        r_net=round(r_net, 4), reason=reason, legs=market_legs,
    )


def _b_levels(b: dict, direction: str, b_geo: str) -> tuple[float, float] | None:
    """Trigger/stop del Setup B secondo la variante geometrica.

    MAX_STOP_ATR=2.5 resta adeguato: stop15 fissa la distanza a 1.5*ATR;
    buf/both devono comunque passare il check di geometria."""
    if b_geo == "base":
        if not b["geo_ok"]:
            return None
        return b["trigger"], b["stop"]  # livelli identici al motore live

    a, rh, rl = b["atr"], b["rng_high"], b["rng_low"]
    if direction == "long":
        trig = rh + 0.25 * a if b_geo in ("buf", "both") else float(b["trigger"])
        stop = (trig - 1.5 * a) if b_geo in ("stop15", "both") else max(trig - a, rl)
    else:
        trig = rl - 0.25 * a if b_geo in ("buf", "both") else float(b["trigger"])
        stop = (trig + 1.5 * a) if b_geo in ("stop15", "both") else min(trig + a, rh)
    if abs(trig - stop) > MAX_STOP_ATR * a or abs(trig - stop) <= 0:
        return None
    return _round_px(trig), _round_px(stop)


def simulate(
    data: dict[str, pd.DataFrame],
    table: dict,
    cfg: Config,
    aux: dict,
) -> list[TradeRec]:
    trades: list[TradeRec] = []
    rs_on = cfg.rs_mode == "on" or (cfg.rs_mode == "cond" and len(data) >= RS_MIN_UNIVERSE)

    for sym, df in data.items():
        idx = df.index
        o = df["open"].to_numpy(); h = df["high"].to_numpy()
        low = df["low"].to_numpy(); c = df["close"].to_numpy()
        atr_arr = aux["atr"][sym]; e20_arr = aux["e20"][sym]
        pos: dict | None = None
        legs: list = []

        for i in range(MIN_BARS, len(df)):
            if pos is not None:
                closed = _step_exit(pos, legs, i, o, h, low, c, atr_arr, e20_arr, idx)
                if closed:
                    trades.append(_finish(pos, legs))
                    pos, legs = None, []
                continue

            date = idx[i]
            if date < START:
                continue
            info = table.get((sym, idx[i - 1]))
            if info is None:
                continue
            direction = info["trend"]
            if rs_on and info["cand"] != direction:
                continue
            if cfg.f_regime and info["regime"] != direction:
                continue
            if cfg.f_rvol and info["rvol"] < RVOL_INTEREST:
                continue
            if info["a"] is not None:
                setup, trig, stop = "A", info["a"]["trigger"], info["a"]["stop"]
            elif info["b"] is not None:
                levels = _b_levels(info["b"], direction, cfg.b_geo)
                if levels is None:
                    continue
                setup, (trig, stop) = "B", levels
            else:
                continue

            sign = 1.0 if direction == "long" else -1.0
            if cfg.f_confirm:
                # PROXY conferma 4H: la barra daily deve CHIUDERE oltre il
                # trigger; fill alla chiusura (eseguibile in reale).
                if not (sign * (c[i] - trig) > 0):
                    continue
                fill = float(c[i])
            else:
                if direction == "long":
                    if h[i] < trig:
                        continue
                    fill = max(trig, float(o[i]))
                else:
                    if low[i] > trig:
                        continue
                    fill = min(trig, float(o[i]))

            runit = sign * (fill - stop)
            if runit <= 0:
                continue
            sizing = position_size(CAPITAL, RISK_PCT, fill, stop,
                                   direction=direction, market="crypto")
            if "error" in sizing:
                continue
            pos = {
                "symbol": sym, "setup": setup, "dir": direction, "sign": sign,
                "signal_date": idx[i - 1], "entry_date": date, "entry": fill,
                "stop0": stop, "stop_cur": stop, "runit": runit,
                "tp1": fill + sign * runit, "tgt": fill + sign * 2 * runit,
                "size": float(sizing["size_units"]),
                "risk_amt": float(sizing["risk_amount"]),
                "frac": 1.0, "tp1_done": False, "trail": None,
                "mode": cfg.exit_mode,
            }
            legs = []
            # stop sulla barra di entry (solo fill a trigger; mai col confirm)
            if not cfg.f_confirm and sign * (stop - (low[i] if direction == "long" else h[i])) >= 0:
                legs.append((1.0, stop, date, "stop_same_bar"))
                trades.append(_finish(pos, legs))
                pos, legs = None, []

        if pos is not None and legs_realized(legs):
            # quota già incassata: chiudo il resto all'ultimo close ("eof")
            legs.append((pos["frac"], float(c[-1]), idx[-1], "eof"))
            trades.append(_finish(pos, legs))

    trades.sort(key=lambda t: t.entry_date)
    return trades


def legs_realized(legs: list) -> bool:
    return len(legs) > 0


def _step_exit(pos, legs, i, o, h, low, c, atr_arr, e20_arr, idx) -> bool:
    """Gestisce la barra i per la posizione aperta. True se completamente chiusa."""
    sign = pos["sign"]
    date = idx[i]
    oi, hi, li, ci = float(o[i]), float(h[i]), float(low[i]), float(c[i])
    hi_fav = hi if sign > 0 else li      # estremo favorevole
    lo_adv = li if sign > 0 else hi      # estremo avverso

    def hit_below(level):  # il prezzo avverso raggiunge level
        return sign * (level - lo_adv) >= 0

    def hit_above(level):  # il prezzo favorevole raggiunge level
        return sign * (hi_fav - level) >= 0

    def gap_below(level):
        return sign * (level - oi) >= 0

    def gap_above(level):
        return sign * (oi - level) >= 0

    if pos["mode"] == "allout":
        if gap_below(pos["stop_cur"]):
            legs.append((1.0, oi, date, "stop_gap")); return True
        if hit_below(pos["stop_cur"]):
            legs.append((1.0, pos["stop_cur"], date, "stop")); return True
        if gap_above(pos["tgt"]):
            legs.append((1.0, oi, date, "target_gap")); return True
        if hit_above(pos["tgt"]):
            legs.append((1.0, pos["tgt"], date, "target")); return True
        return False

    if not pos["tp1_done"]:
        if gap_below(pos["stop_cur"]):
            legs.append((1.0, oi, date, "stop_gap")); return True
        if hit_below(pos["stop_cur"]):  # pessimistico: stop prima del TP1
            legs.append((1.0, pos["stop_cur"], date, "stop")); return True
        if hit_above(pos["tp1"]):
            px1 = oi if gap_above(pos["tp1"]) else pos["tp1"]
            legs.append((0.5, px1, date, "tp1"))
            pos["frac"], pos["tp1_done"] = 0.5, True
            if pos["mode"] == "be":
                pos["stop_cur"] = pos["entry"]
                # pessimistico: se nella stessa barra il prezzo torna a BE,
                # il resto chiude a BE; il target non si prende sulla barra TP1
                if hit_below(pos["stop_cur"]):
                    legs.append((0.5, pos["stop_cur"], date, "be")); return True
            else:  # trail
                pos["trail"] = hi_fav - sign * float(atr_arr[i])
                if sign * (pos["trail"] - pos["stop0"]) < 0:
                    pos["trail"] = pos["stop0"]
                if hit_below(pos["trail"]):
                    legs.append((0.5, pos["trail"], date, "trail")); return True
                if sign * (ci - float(e20_arr[i])) < 0:
                    legs.append((0.5, ci, date, "ema20")); return True
            return False
        return False

    # resto della posizione dopo il TP1
    if pos["mode"] == "be":
        if gap_below(pos["stop_cur"]):
            legs.append((0.5, oi, date, "be_gap")); return True
        if hit_below(pos["stop_cur"]):
            legs.append((0.5, pos["stop_cur"], date, "be")); return True
        if gap_above(pos["tgt"]):
            legs.append((0.5, oi, date, "target_gap")); return True
        if hit_above(pos["tgt"]):
            legs.append((0.5, pos["tgt"], date, "target")); return True
        return False

    # trail: chandelier 1*ATR dai massimi post-TP1 + uscita a close sotto EMA20
    if gap_below(pos["trail"]):
        legs.append((0.5, oi, date, "trail_gap")); return True
    if hit_below(pos["trail"]):
        legs.append((0.5, pos["trail"], date, "trail")); return True
    if sign * (ci - float(e20_arr[i])) < 0:
        legs.append((0.5, ci, date, "ema20")); return True
    new_trail = hi_fav - sign * float(atr_arr[i])
    if sign * (new_trail - pos["trail"]) > 0:
        pos["trail"] = new_trail
    return False


# ---------------------------------------------------------------------------
# Metriche e report
# ---------------------------------------------------------------------------


def agg(trades: list[TradeRec]) -> dict:
    n = len(trades)
    if n == 0:
        return {"n": 0}
    rs = [t.r_net for t in trades]
    wins = sum(1 for r in rs if r > 0)
    nonneg = sum(1 for r in rs if r >= 0)
    lo, hi = wilson_ci(wins, n)
    gw = sum(r for r in rs if r > 0)
    gl = -sum(r for r in rs if r < 0)
    eq = peak = dd = 0.0
    for r in rs:
        eq += r
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
    return {
        "n": n, "wr": wins / n, "ci": (lo, hi), "wr_acc": nonneg / n,
        "exp": sum(rs) / n, "pf": (gw / gl) if gl > 0 else float("inf"),
        "dd": dd, "tot": sum(rs),
    }


def is_trades(trades: list[TradeRec]) -> list[TradeRec]:
    return [t for t in trades if t.entry_date < SPLIT]


def oos_trades(trades: list[TradeRec]) -> list[TradeRec]:
    return [t for t in trades if t.entry_date >= SPLIT]


def fmt(label: str, trades: list[TradeRec], extra: str = "") -> str:
    a = agg(trades)
    if a["n"] == 0:
        return f"{label:34s} n=   0  —"
    lo, hi = a["ci"]
    pf = f"{a['pf']:.2f}" if a["pf"] != float("inf") else "inf"
    return (f"{label:34s} n={a['n']:4d}  WR={a['wr']*100:5.1f}% (CI {lo*100:.0f}-{hi*100:.0f}%)  "
            f"exp={a['exp']:+.3f}R  PF={pf}  DD={a['dd']:.1f}R{extra}")


def by_setup_lines(trades: list[TradeRec], indent: str = "    ") -> None:
    for s in ("A", "B"):
        sub = [t for t in trades if t.setup == s]
        print(indent + fmt(f"setup {s}", sub))


def elimination_stats(base_is: list[TradeRec], var_is: list[TradeRec]) -> str:
    key = lambda t: (t.symbol, t.signal_date)
    vk = {key(t) for t in var_is}
    removed = [t for t in base_is if key(t) not in vk]
    kept = [t for t in base_is if key(t) in vk]
    bk = {key(t) for t in base_is}
    added = [t for t in var_is if key(t) not in bk]
    exp_rm = statistics.mean([t.r_net for t in removed]) if removed else float("nan")
    exp_kp = statistics.mean([t.r_net for t in kept]) if kept else float("nan")
    out = (f"eliminati {len(removed)} (exp {exp_rm:+.3f}R) | "
           f"tenuti {len(kept)} (exp {exp_kp:+.3f}R)")
    if added:
        out += f" | nuovi {len(added)}"
    return out


# ---------------------------------------------------------------------------
# Parti
# ---------------------------------------------------------------------------


_ENV: dict = {}
TESTED: set[str] = set()


def env() -> tuple[dict, dict, dict]:
    if not _ENV:
        data = load_data()
        bench = data["BTCUSDT"]
        print(f"Universo fisso: {len(data)} simboli, dati <= {DATA_END.date()} (cache diag_cache/)")
        table = build_signal_table(data, bench)
        aux = {
            "atr": {s: atr_fn(df).to_numpy() for s, df in data.items()},
            "e20": {s: ema(df["close"], 20).to_numpy() for s, df in data.items()},
        }
        _ENV.update(data=data, table=table, aux=aux)
    return _ENV["data"], _ENV["table"], _ENV["aux"]


def run(name: str) -> list[TradeRec]:
    data, table, aux = env()
    TESTED.add(name)
    return simulate(data, table, make_config(name), aux)


def part1() -> None:
    print("\n" + "=" * 78)
    print("PARTE 1 — Ablazione filtri (SOLO IN-SAMPLE, entry < 2025-01-01)")
    print("=" * 78)
    base = run("base")
    base_is = is_trades(base)
    print(fmt("(1) base (=run 208 trade)", base_is))
    by_setup_lines(base_is)

    singles = ["regime", "confirm", "rs-cond", "rvol"]
    results: dict[str, list[TradeRec]] = {"base": base}
    base_exp = agg(base_is)["exp"]
    improvers: list[str] = []
    notes = {
        "regime": "long solo regime long, short solo short, mai in mixed",
        "confirm": "PROXY 4H: entry solo se il daily CHIUDE oltre il trigger (fill a close)",
        "rs-cond": f"gate RS attivo solo con universo >={RS_MIN_UNIVERSE} (qui 23 -> identico a base)",
        "rvol": f"candidato solo con RVOL >= {RVOL_INTEREST} alla barra-segnale",
    }
    for name in singles:
        tr = run(name)
        results[name] = tr
        tis = is_trades(tr)
        print("\n" + fmt(f"(+) {name}", tis))
        print(f"      {notes[name]}")
        print(f"      {elimination_stats(base_is, tis)}")
        by_setup_lines(tis, "      ")
        delta = agg(tis)["exp"] - base_exp if agg(tis)["n"] else float("nan")
        print(f"      delta expectancy IS vs base: {delta:+.3f}R")
        if agg(tis)["n"] and delta >= 0.05:
            improvers.append(name)

    print("\n(6) Filtri che migliorano l'expectancy IS di almeno +0.05R:",
          improvers or "nessuno")
    combos = []
    if len(improvers) >= 2:
        from itertools import combinations
        for k in range(2, len(improvers) + 1):
            combos += ["+".join(c) for c in combinations(improvers, k)]
    for name in combos:
        tis = is_trades(run(name))
        print(fmt(f"    combo {name}", tis))
        print(f"      {elimination_stats(base_is, tis)}")
        by_setup_lines(tis, "      ")
    print("\n(info) contributo marginale del gate RS (variante informativa):")
    print(fmt("    rs-off (solo trend EMA50)", is_trades(run("rs-off"))))

    # Tabella riassuntiva Parte 1
    print("\n--- TABELLA RIASSUNTIVA PARTE 1 (IS) ---")
    for name in ["base"] + singles + combos + ["rs-off"]:
        tis = is_trades(results.get(name) or run(name))
        print(fmt(name, tis))
        by_setup_lines(tis, "  ")


def part2() -> None:
    print("\n" + "=" * 78)
    print("PARTE 2 — Geometria Setup B (SOLO IN-SAMPLE)")
    print("=" * 78)
    variants = {
        "base": "stop = max(trigger-ATR, rng_low) [attuale]",
        "bstop15": "(a) stop = trigger -/+ 1.5*ATR",
        "bbuf": "(b) trigger = rng_high/low +/- 0.25*ATR (stop formula originale)",
        "bgeo-both": "(c) entrambi",
    }
    for name, desc in variants.items():
        tis = is_trades(run(name))
        b = [t for t in tis if t.setup == "B"]
        eb = sum(1 for t in tis if "stop_same_bar" in t.reason)
        eb_pct = eb / len(tis) * 100 if tis else 0.0
        print(f"\n{name}: {desc}")
        print(fmt("  tutti i trade", tis, f"  | entry-bar stop-out {eb}/{len(tis)} ({eb_pct:.0f}%)"))
        by_setup_lines(tis, "  ")
        if b:
            eb_b = sum(1 for t in b if "stop_same_bar" in t.reason)
            print(f"    (solo B: entry-bar stop-out {eb_b}/{len(b)} = {eb_b/len(b)*100:.0f}%)")


def part3() -> None:
    print("\n" + "=" * 78)
    print("PARTE 3 — Gestione dell'uscita (SOLO IN-SAMPLE)")
    print("=" * 78)
    variants = {
        "base": "(a) all-out a 2R [attuale]",
        "exit-be": "(b) TP 50% a 1R + stop a breakeven sul resto, target 2R",
        "exit-trail": "(c) TP 50% a 1R + trailing 1*ATR (uscita alternativa: close < EMA20)",
    }
    for name, desc in variants.items():
        tis = is_trades(run(name))
        a = agg(tis)
        print(f"\n{name}: {desc}")
        print(fmt("  tutti i trade", tis))
        if a["n"]:
            print(f"    WR contabile (r_net >= 0): {a['wr_acc']*100:.1f}%   totale {a['tot']:+.1f}R")
        by_setup_lines(tis, "  ")
        from collections import Counter
        dist = Counter(t.reason for t in tis)
        top = ", ".join(f"{k}:{v}" for k, v in dist.most_common(8))
        print(f"    distribuzione esiti: {top}")


def part4() -> None:
    print("\n" + "=" * 78)
    print("PARTE 4 — Sintesi (scelta su IS) e validazione OOS (UNICA lettura)")
    print("=" * 78)
    base = run("base")
    base_is = is_trades(base)
    base_exp = agg(base_is)["exp"]

    singles = ["regime", "confirm", "rs-cond", "rvol"]
    improvers = []
    for name in singles:
        a = agg(is_trades(run(name)))
        if a["n"] and a["exp"] - base_exp >= 0.05:
            improvers.append(name)
    filter_sets: list[str] = [""]
    filter_sets += improvers
    if len(improvers) >= 2:
        from itertools import combinations
        for k in range(2, len(improvers) + 1):
            filter_sets += ["+".join(c) for c in combinations(improvers, k)]

    geos = ["", "bstop15", "bbuf", "bgeo-both"]
    exits = ["", "exit-be", "exit-trail"]
    candidates: dict[str, dict] = {}
    for fs in filter_sets:
        for g in geos:
            for e in exits:
                parts = [p for p in (fs, g, e) if p]
                name = "+".join(parts) if parts else "base"
                a = agg(is_trades(run(name)))
                candidates[name] = a

    eligible = {k: v for k, v in candidates.items() if v.get("n", 0) >= 80}
    print(f"\nConfigurazioni valutate in PARTE 4: {len(candidates)} "
          f"(idonee con n_IS >= 80: {len(eligible)})")
    ranked = sorted(eligible.items(), key=lambda kv: kv[1]["exp"], reverse=True)
    print("\nClassifica IN-SAMPLE (top 10, exp decrescente):")
    for name, a in ranked[:10]:
        lo, hi = a["ci"]
        pf = f"{a['pf']:.2f}" if a["pf"] != float("inf") else "inf"
        print(f"  {name:34s} n={a['n']:4d} WR={a['wr']*100:5.1f}% (CI {lo*100:.0f}-{hi*100:.0f}%) "
              f"exp={a['exp']:+.3f}R PF={pf} DD={a['dd']:.1f}R")

    if not ranked:
        print("Nessuna configurazione con n_IS >= 80: niente lettura OOS.")
        return
    best_name = ranked[0][0]
    best = run(best_name)
    bis, boos = is_trades(best), oos_trades(best)
    print(f"\nCONFIGURAZIONE SCELTA (miglior expectancy IS, n>=80): {best_name}")
    print(fmt("  IS ", bis))
    by_setup_lines(bis, "  ")
    a_is = agg(bis)
    print(f"    WR contabile IS: {a_is['wr_acc']*100:.1f}%  totale {a_is['tot']:+.1f}R")

    print("\n--- LETTURA OUT-OF-SAMPLE (unica) ---")
    print(fmt("  OOS", boos))
    by_setup_lines(boos, "  ")
    a_oos = agg(boos)
    if a_oos["n"]:
        print(f"    WR contabile OOS: {a_oos['wr_acc']*100:.1f}%  totale {a_oos['tot']:+.1f}R")
    exp_is, exp_oos = a_is["exp"], a_oos.get("exp", float("nan"))
    print(f"\nConfronto: exp IS {exp_is:+.3f}R vs exp OOS {exp_oos:+.3f}R")
    if a_oos.get("n", 0) == 0:
        print("VERDETTO: nessun trade OOS — non valutabile.")
    elif exp_oos > 0 and (exp_is <= 0 or exp_oos >= 0.5 * exp_is):
        print("VERDETTO: OOS positivo ed entro il 50% di degrado -> candidata al forward.")
    elif exp_oos > 0:
        print("VERDETTO: OOS positivo ma degrado > 50% vs IS -> debole, probabile fit del rumore.")
    else:
        print("VERDETTO: OOS negativo -> abbiamo fittato il rumore. La configurazione NON è candidata.")

    print(f"\nAVVERTENZE: (1) survivorship bias: universo = costituenti ATTUALI della")
    print("top 30; i token delistati/decaduti non sono nel campione, i risultati")
    print("sono ottimistici. (2) Multiple testing: varianti totali simulate in")
    print(f"questa sessione: {len(TESTED)} — con ~{len(TESTED)} tentativi una expectancy IS")
    print("marginalmente positiva può essere fortuna; solo il forward test conta.")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] == "list":
        print(__doc__)
        print("Varianti atomiche:", ", ".join(ATOMS))
        return
    cmd = args[0]
    if cmd == "rebuild-cache":
        for f in CACHE.glob("*.pkl"):
            f.unlink()
        env()
        print("Cache rigenerata.")
        return
    if cmd == "run":
        for name in args[1:]:
            tis = is_trades(run(name))
            print(fmt(name + " (IS)", tis))
            by_setup_lines(tis, "  ")
        return
    parts = {"part1": [part1], "part2": [part2], "part3": [part3], "part4": [part4],
             "all": [part1, part2, part3, part4]}
    if cmd not in parts:
        raise SystemExit(f"comando sconosciuto: {cmd}")
    for p in parts[cmd]:
        p()


if __name__ == "__main__":
    main()
