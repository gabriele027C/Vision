"""Selezione asset (§3): forza relativa vs benchmark + RVOL + filtro trend."""
import pandas as pd

from config import RS_BOTTOM_PERCENTILE, RS_TOP_PERCENTILE
from engine.indicators import ema, pct_return, rvol


def rs_scores(data: dict[str, pd.DataFrame], bench: pd.DataFrame) -> dict[str, float]:
    """Score 0..1 = rank percentile della sovraperformance a 20 e 60 giorni vs benchmark."""
    b20 = pct_return(bench["close"], 20)
    b60 = pct_return(bench["close"], 60)
    raw: dict[str, float] = {}
    for sym, df in data.items():
        r20 = pct_return(df["close"], 20) - b20
        r60 = pct_return(df["close"], 60) - b60
        raw[sym] = 0.5 * r20 + 0.5 * r60
    if not raw:
        return {}
    s = pd.Series(raw)
    ranks = s.rank(pct=True)
    return {sym: float(ranks[sym]) for sym in raw}


def resolve_candidate_direction(
    score: float,
    last: float,
    e50: float,
    long_allowed: bool,
    short_allowed: bool,
) -> str | None:
    """Direzione candidata screener — stessa logica di classify_candidates."""
    if long_allowed and score >= RS_TOP_PERCENTILE and last > e50:
        return "long"
    if short_allowed and score <= RS_BOTTOM_PERCENTILE and last < e50:
        return "short"
    return None


def natural_direction(score: float, last: float, e50: float) -> str | None:
    """Direzione 'naturale' da RS + trend EMA50, indipendente dal regime."""
    if score >= RS_TOP_PERCENTILE and last > e50:
        return "long"
    if score <= RS_BOTTOM_PERCENTILE and last < e50:
        return "short"
    return None


def classify_candidates(
    data: dict[str, pd.DataFrame],
    scores: dict[str, float],
    long_allowed: bool,
    short_allowed: bool,
) -> list[dict]:
    """Candidati long (top 20% RS, sopra EMA50) e short (bottom 20%, sotto EMA50)."""
    out: list[dict] = []
    for sym, df in data.items():
        score = scores.get(sym)
        if score is None or len(df) < 220:
            continue
        close = df["close"]
        last = float(close.iloc[-1])
        e50 = float(ema(close, 50).iloc[-1])
        rv_series = rvol(df["volume"])
        rv = float(rv_series.iloc[-1]) if pd.notna(rv_series.iloc[-1]) else 0.0

        direction = resolve_candidate_direction(score, last, e50, long_allowed, short_allowed)
        if direction is None:
            continue
        out.append(
            {
                "symbol": sym,
                "direction": direction,
                "rs_score": round(score, 3),
                "rvol": round(rv, 2),
                "last_price": last,
            }
        )
    # I long più forti e gli short più deboli per primi.
    out.sort(key=lambda c: c["rs_score"] if c["direction"] == "short" else -c["rs_score"])
    return out
