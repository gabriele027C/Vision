"""Backtester event-driven per i Setup A/B — riusa detection e screener di produzione.

Principi:
- Nessun look-ahead: a ogni barra i il segnale è calcolato su df.iloc[:i]
  (solo barre chiuse prima della barra simulata) e i fill avvengono sulla
  barra i stessa.
- Riuso esatto: detect_setup_a / detect_setup_b / rs_scores /
  classify_candidates sono le stesse funzioni dello scanner live; qui non
  esiste logica di setup duplicata.
- Fill realistici: entry quando la barra supera il trigger, al max(trigger,
  open) per i long e min(trigger, open) per gli short — i gap oltre il
  trigger fillano all'open. Stop con gap-through (open oltre lo stop filla
  all'open). Target 2R. Time-stop opzionale a N barre (uscita in chiusura).
- Costi per mercato: crypto taker 0.055% per lato + funding stimato dalla
  durata; stocks 0.01$/share (min 1$) per lato + slippage 0.05% per lato.

LIMITE NOTO (survivorship bias): l'universo stocks usa i costituenti ATTUALI
di S&P 500 / Nasdaq 100 — i titoli rimossi dagli indici (spesso i peggiori)
non sono nel campione, quindi i risultati sui titoli azionari sono ottimistici.
Il report lo stampa come avvertenza. Il percorso crypto non ne soffre finché
i simboli richiesti esistono per tutto il periodo.

CLI:
    python -m engine.backtest --market crypto --symbols BTCUSDT,ETHUSDT --start 2022-01-01
    opzioni: --end, --capital, --risk-pct, --time-stop, --split (walk-forward IS/OOS)
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass, field

import pandas as pd

from engine.screener import classify_candidates, rs_scores
from engine.setups import detect_setup_a, detect_setup_b
from engine.sizing import position_size

MIN_BARS = 220  # storico minimo per la detection (coerente con i setup)

# --- Costi default ---
CRYPTO_TAKER_FEE = 0.00055        # 0.055% per lato
CRYPTO_FUNDING_DAILY = 0.0003     # stima 0.01% per 8h * 3 periodi/giorno
STOCK_COMMISSION_PER_SHARE = 0.01
STOCK_MIN_COMMISSION = 1.0
STOCK_SLIPPAGE_PCT = 0.0005       # 0.05% per lato


@dataclass
class Trade:
    symbol: str
    market: str
    setup: str
    direction: str
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry: float
    exit: float
    exit_reason: str
    bars_held: int
    r_gross: float
    cost_r: float
    r_net: float


@dataclass
class _Position:
    symbol: str
    setup: str
    direction: str
    entry_date: pd.Timestamp
    entry: float
    stop: float
    target: float
    risk_per_unit: float
    size_units: float
    risk_amount: float
    notional: float
    bars_held: int = 0


# ---------------------------------------------------------------------------
# Fill / exit — funzioni pure, testabili in isolamento
# ---------------------------------------------------------------------------


def check_entry(bar: pd.Series, direction: str, trigger: float) -> float | None:
    """Fill di entrata sulla barra corrente, None se il trigger non è superato.

    Gap oltre il trigger → fill all'open (non al trigger)."""
    if direction == "long":
        if bar["high"] >= trigger:
            return max(trigger, float(bar["open"]))
    else:
        if bar["low"] <= trigger:
            return min(trigger, float(bar["open"]))
    return None


def check_exit(
    bar: pd.Series, pos: _Position, time_stop: int | None
) -> tuple[float, str] | None:
    """Uscita sulla barra corrente: stop (con gap-through), target 2R, time-stop.

    Ordine pessimistico: lo stop è verificato prima del target quando entrambi
    i livelli cadono nella stessa barra."""
    o, h, low = float(bar["open"]), float(bar["high"]), float(bar["low"])
    if pos.direction == "long":
        if o <= pos.stop:
            return o, "stop_gap"
        if low <= pos.stop:
            return pos.stop, "stop"
        if o >= pos.target:
            return o, "target_gap"
        if h >= pos.target:
            return pos.target, "target"
    else:
        if o >= pos.stop:
            return o, "stop_gap"
        if h >= pos.stop:
            return pos.stop, "stop"
        if o <= pos.target:
            return o, "target_gap"
        if low <= pos.target:
            return pos.target, "target"
    if time_stop is not None and pos.bars_held >= time_stop:
        return float(bar["close"]), "time"
    return None


def trade_costs(
    market: str,
    entry: float,
    exit_px: float,
    size_units: float,
    days_held: float,
    *,
    taker_fee: float = CRYPTO_TAKER_FEE,
    funding_daily: float = CRYPTO_FUNDING_DAILY,
    commission_per_share: float = STOCK_COMMISSION_PER_SHARE,
    min_commission: float = STOCK_MIN_COMMISSION,
    slippage_pct: float = STOCK_SLIPPAGE_PCT,
) -> float:
    """Costi round-trip in valuta per il mercato."""
    if market == "crypto":
        fees = taker_fee * size_units * (entry + exit_px)
        funding = funding_daily * size_units * entry * max(days_held, 0.0)
        return fees + funding
    commission = 2 * max(commission_per_share * size_units, min_commission)
    slippage = slippage_pct * size_units * (entry + exit_px)
    return commission + slippage


# ---------------------------------------------------------------------------
# Simulazione per simbolo (signal_fn iniettabile per i test)
# ---------------------------------------------------------------------------


def simulate_symbol(
    df: pd.DataFrame,
    signal_fn,
    *,
    market: str,
    symbol: str,
    capital: float = 10_000.0,
    risk_pct: float = 1.0,
    time_stop: int | None = None,
    start: pd.Timestamp | None = None,
    end: pd.Timestamp | None = None,
    cost_kwargs: dict | None = None,
) -> list[Trade]:
    """Itera barra per barra: signal_fn(hist, date) → segnale dict o None.

    Il segnale deve contenere direction, entry_trigger, stop, setup — cioè
    l'output di detect_setup_a/b più la direzione dello screener."""
    trades: list[Trade] = []
    pos: _Position | None = None
    cost_kwargs = cost_kwargs or {}

    for i in range(MIN_BARS, len(df)):
        bar = df.iloc[i]
        date = df.index[i]
        if end is not None and date > end:
            break

        if pos is not None:
            pos.bars_held += 1
            hit = check_exit(bar, pos, time_stop)
            if hit is not None:
                exit_px, reason = hit
                trades.append(
                    _close_trade(pos, exit_px, reason, date, market, cost_kwargs)
                )
                pos = None
            continue

        if start is not None and date < start:
            continue

        hist = df.iloc[:i]
        sig = signal_fn(hist, date)
        if sig is None:
            continue
        direction = sig["direction"]
        fill = check_entry(bar, direction, float(sig["entry_trigger"]))
        if fill is None:
            continue

        stop = float(sig["stop"])
        risk_per_unit = abs(fill - stop)
        if risk_per_unit <= 0:
            continue
        sizing = position_size(
            capital, risk_pct, fill, stop, direction=direction, market=market
        )
        if "error" in sizing:
            continue  # es. stop oltre liquidazione: il trade non è operabile
        target = fill + 2 * risk_per_unit if direction == "long" else fill - 2 * risk_per_unit
        pos = _Position(
            symbol=symbol,
            setup=sig["setup"],
            direction=direction,
            entry_date=date,
            entry=fill,
            stop=stop,
            target=target,
            risk_per_unit=risk_per_unit,
            size_units=float(sizing["size_units"]),
            risk_amount=float(sizing["risk_amount"]),
            notional=float(sizing["notional"]),
        )
        # Stop-out nella stessa barra di entrata (pessimistico, niente target same-bar).
        same_bar = (
            (direction == "long" and float(bar["low"]) <= stop)
            or (direction == "short" and float(bar["high"]) >= stop)
        )
        if same_bar:
            trades.append(_close_trade(pos, stop, "stop_same_bar", date, market, cost_kwargs))
            pos = None

    return trades


def _close_trade(
    pos: _Position,
    exit_px: float,
    reason: str,
    date: pd.Timestamp,
    market: str,
    cost_kwargs: dict,
) -> Trade:
    sign = 1.0 if pos.direction == "long" else -1.0
    r_gross = sign * (exit_px - pos.entry) / pos.risk_per_unit
    days = max((date - pos.entry_date).total_seconds() / 86_400.0, 0.0)
    cost = trade_costs(market, pos.entry, exit_px, pos.size_units, days, **cost_kwargs)
    cost_r = cost / pos.risk_amount if pos.risk_amount > 0 else 0.0
    return Trade(
        symbol=pos.symbol,
        market=market,
        setup=pos.setup,
        direction=pos.direction,
        entry_date=pos.entry_date,
        exit_date=date,
        entry=pos.entry,
        exit=exit_px,
        exit_reason=reason,
        bars_held=pos.bars_held,
        r_gross=round(r_gross, 4),
        cost_r=round(cost_r, 4),
        r_net=round(r_gross - cost_r, 4),
    )


# ---------------------------------------------------------------------------
# Segnali di produzione: screener cross-sectional + detect A/B
# ---------------------------------------------------------------------------


def build_production_signal_fn(
    symbol: str, data: dict[str, pd.DataFrame], bench: pd.DataFrame
):
    """signal_fn che replica lo scanner: RS + classify_candidates + Setup A/B.

    Il regime di mercato non è applicato (long e short sempre consentiti):
    il backtest misura l'edge di screener+setup, non il filtro di regime."""

    def signal_fn(hist: pd.DataFrame, date: pd.Timestamp):
        slices = {s: d.loc[d.index < date] for s, d in data.items()}
        slices = {s: d for s, d in slices.items() if len(d) >= MIN_BARS}
        if symbol not in slices:
            return None
        bench_slice = bench.loc[bench.index < date]
        if len(bench_slice) < MIN_BARS:
            return None
        scores = rs_scores(slices, bench_slice)
        candidates = classify_candidates(slices, scores, True, True)
        cand = next((c for c in candidates if c["symbol"] == symbol), None)
        if cand is None:
            return None
        direction = cand["direction"]
        setup = detect_setup_a(hist, direction) or detect_setup_b(hist, direction)
        if setup is None:
            return None
        return {**setup, "direction": direction}

    return signal_fn


# ---------------------------------------------------------------------------
# Aggregati
# ---------------------------------------------------------------------------


def wilson_ci(wins: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervallo di confidenza di Wilson al 95% per la win rate."""
    if n == 0:
        return (0.0, 0.0)
    p = wins / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def aggregate(trades: list[Trade]) -> dict:
    n = len(trades)
    if n == 0:
        return {"n_trades": 0}
    rs = [t.r_net for t in trades]
    wins = sum(1 for r in rs if r > 0)
    ci_lo, ci_hi = wilson_ci(wins, n)
    gross_win = sum(r for r in rs if r > 0)
    gross_loss = -sum(r for r in rs if r < 0)
    cum = 0.0
    peak = 0.0
    max_dd = 0.0
    for r in rs:
        cum += r
        peak = max(peak, cum)
        max_dd = max(max_dd, peak - cum)
    return {
        "n_trades": n,
        "wins": wins,
        "win_rate": round(wins / n, 4),
        "win_rate_ci95": (round(ci_lo, 4), round(ci_hi, 4)),
        "expectancy_r": round(sum(rs) / n, 4),
        "profit_factor": round(gross_win / gross_loss, 3) if gross_loss > 0 else float("inf"),
        "max_drawdown_r": round(max_dd, 3),
        "total_r": round(sum(rs), 3),
        "avg_bars_held": round(sum(t.bars_held for t in trades) / n, 1),
    }


def aggregate_by(trades: list[Trade], key: str) -> dict[str, dict]:
    groups: dict[str, list[Trade]] = {}
    for t in trades:
        groups.setdefault(getattr(t, key), []).append(t)
    return {k: aggregate(v) for k, v in sorted(groups.items())}


def format_report(
    trades: list[Trade],
    *,
    market: str,
    split: pd.Timestamp | None = None,
    label: str = "",
) -> str:
    lines: list[str] = []
    title = f"BACKTEST {market.upper()}" + (f" — {label}" if label else "")
    lines.append("=" * 64)
    lines.append(title)
    lines.append("=" * 64)
    if market == "stocks":
        lines.append(
            "⚠ AVVERTENZA SURVIVORSHIP BIAS: universo = costituenti ATTUALI degli"
            "\n  indici; i titoli rimossi non sono nel campione. Risultati ottimistici."
        )

    def block(name: str, ts: list[Trade]) -> None:
        agg = aggregate(ts)
        lines.append(f"\n--- {name} ({agg.get('n_trades', 0)} trade) ---")
        if agg.get("n_trades", 0) == 0:
            lines.append("nessun trade")
            return
        lo, hi = agg["win_rate_ci95"]
        lines.append(
            f"win rate     : {agg['win_rate']*100:.1f}%  (CI95 Wilson {lo*100:.1f}%–{hi*100:.1f}%)"
        )
        lines.append(f"expectancy   : {agg['expectancy_r']:+.3f} R/trade")
        pf = agg["profit_factor"]
        lines.append(f"profit factor: {pf if pf != float('inf') else 'inf'}")
        lines.append(f"max drawdown : {agg['max_drawdown_r']:.2f} R")
        lines.append(f"totale       : {agg['total_r']:+.2f} R   (barre medie {agg['avg_bars_held']})")
        for dim in ("setup", "symbol"):
            sub = aggregate_by(ts, dim)
            if len(sub) > 1:
                for k, a in sub.items():
                    lines.append(
                        f"  {dim}={k}: n={a['n_trades']} WR={a['win_rate']*100:.0f}% "
                        f"exp={a['expectancy_r']:+.2f}R PF={a['profit_factor']}"
                    )

    block("TOTALE", trades)
    if split is not None:
        is_trades = [t for t in trades if t.entry_date < split]
        oos_trades = [t for t in trades if t.entry_date >= split]
        block(f"IN-SAMPLE (< {split.date()})", is_trades)
        block(f"OUT-OF-SAMPLE (>= {split.date()})", oos_trades)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Orchestrazione + CLI
# ---------------------------------------------------------------------------


def run_backtest(
    market: str,
    symbols: list[str],
    start: pd.Timestamp,
    end: pd.Timestamp | None = None,
    *,
    capital: float = 10_000.0,
    risk_pct: float = 1.0,
    time_stop: int | None = None,
) -> list[Trade]:
    """Scarica i dati dai client esistenti e simula tutti i simboli."""
    warmup = start - pd.Timedelta(days=400)  # 220 barre + buffer weekend/festivi

    if market == "crypto":
        from data import binance_client

        data: dict[str, pd.DataFrame] = {}
        for sym in symbols:
            df = binance_client.klines_range(sym, "1d", int(warmup.timestamp() * 1000))
            if len(df) > 1:
                data[sym] = df.iloc[:-1]  # scarta la candela in formazione
        bench = data.get("BTCUSDT")
        if bench is None:
            bench = binance_client.klines_range(
                "BTCUSDT", "1d", int(warmup.timestamp() * 1000)
            ).iloc[:-1]
    else:
        from data import stocks_client

        years = max(2, int((pd.Timestamp.now(tz="UTC") - warmup).days / 365) + 1)
        data = stocks_client.daily_history(symbols, period=f"{years}y", threads=False)
        bench_map = stocks_client.daily_history(["SPY"], period=f"{years}y", threads=False, min_bars=50)
        bench = bench_map.get("SPY")
        if bench is None:
            raise RuntimeError("benchmark SPY non disponibile")

    trades: list[Trade] = []
    for sym, df in data.items():
        fn = build_production_signal_fn(sym, data, bench)
        trades.extend(
            simulate_symbol(
                df,
                fn,
                market=market,
                symbol=sym,
                capital=capital,
                risk_pct=risk_pct,
                time_stop=time_stop,
                start=start,
                end=end,
            )
        )
    trades.sort(key=lambda t: t.entry_date)
    return trades


def main() -> None:
    ap = argparse.ArgumentParser(description="Backtest Setup A/B Vision")
    ap.add_argument("--market", choices=["crypto", "stocks"], required=True)
    ap.add_argument("--symbols", required=True, help="lista separata da virgole")
    ap.add_argument("--start", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end", default=None, help="YYYY-MM-DD")
    ap.add_argument("--capital", type=float, default=10_000.0)
    ap.add_argument("--risk-pct", type=float, default=1.0)
    ap.add_argument("--time-stop", type=int, default=None, help="uscita dopo N barre")
    ap.add_argument("--split", default=None, help="data walk-forward IS/OOS (YYYY-MM-DD)")
    args = ap.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    start = pd.Timestamp(args.start, tz="UTC")
    end = pd.Timestamp(args.end, tz="UTC") if args.end else None
    split = pd.Timestamp(args.split, tz="UTC") if args.split else None

    trades = run_backtest(
        args.market,
        symbols,
        start,
        end,
        capital=args.capital,
        risk_pct=args.risk_pct,
        time_stop=args.time_stop,
    )
    print(format_report(trades, market=args.market, split=split))
    print(f"\ntrade totali: {len(trades)}")
    for t in trades:
        print(
            f"{t.entry_date.date()} {t.symbol:10s} {t.setup} {t.direction:5s} "
            f"in={t.entry:.6g} out={t.exit:.6g} ({t.exit_reason:12s}) "
            f"R={t.r_net:+.2f}"
        )


if __name__ == "__main__":
    main()
