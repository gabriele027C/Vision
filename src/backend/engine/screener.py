"""Selezione asset (§3): forza relativa vs benchmark + RVOL + filtro trend."""
import pandas as pd

from config import (
    RS_BOTTOM_PERCENTILE,
    RS_TOP_PERCENTILE,
    RVOL_HARD_FILTER,
    RVOL_INTEREST,
)
from engine.indicators import ema, pct_return, rvol


def rank_score(rs: float, rv: float, direction: str) -> float:
    """Punteggio combinato 0.7*RS + 0.3*RVOL (cappato a 2x la soglia interesse).

    Per gli short la forza RS è speculare (1 - rs): un candidato short è tanto
    più forte quanto più basso è il suo percentile RS; l'RVOL alto premia in
    entrambe le direzioni."""
    strength = rs if direction == "long" else 1.0 - rs
    vol_component = min(rv / RVOL_INTEREST, 2.0) / 2.0
    return 0.7 * strength + 0.3 * vol_component


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
    long_allowed: bool = True,
    short_allowed: bool = True,
) -> str | None:
    """Direzione da trend EMA50 (FASE 2: RS non esclude più).

    long_allowed/short_allowed restano in firma per retrocompatibilità ma
    non filtrano: il regime è solo banner informativo.
    """
    del score, long_allowed, short_allowed  # RS/regime non escludono
    if last > e50:
        return "long"
    if last < e50:
        return "short"
    return None


def natural_direction(score: float, last: float, e50: float) -> str | None:
    """Direzione da trend EMA50; RS usato solo per ordinamento a valle."""
    del score
    if last > e50:
        return "long"
    if last < e50:
        return "short"
    return None


def classify_candidates(
    data: dict[str, pd.DataFrame],
    scores: dict[str, float],
    long_allowed: bool = True,
    short_allowed: bool = True,
    rvol_hard_filter: bool | None = None,
) -> list[dict]:
    """Candidati per trend EMA50, ORDINATI per rank RS (non esclusi da percentile).

    FASE 2: il gate RS percentile non esclude più nulla — il rank_score ordina
    l'attenzione. long_allowed/short_allowed ignorati (regime = banner).
    Con rvol_hard_filter=True i candidati con RVOL < RVOL_INTEREST cadono.
    """
    del long_allowed, short_allowed
    if rvol_hard_filter is None:
        rvol_hard_filter = RVOL_HARD_FILTER
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

        direction = resolve_candidate_direction(score, last, e50)
        if direction is None:
            continue
        if rvol_hard_filter and rv < RVOL_INTEREST:
            continue
        out.append(
            {
                "symbol": sym,
                "direction": direction,
                "rs_score": round(score, 3),
                "rvol": round(rv, 2),
                "last_price": last,
                "rank_score": round(rank_score(score, rv, direction), 4),
            }
        )
    out.sort(key=lambda c: -c["rank_score"])
    return out
