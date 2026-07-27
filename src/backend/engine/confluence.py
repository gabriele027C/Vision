"""Confluence score 0–100: SOLO ordinamento attenzione (FASE 5).

Pesi in CONFLUENCE_WEIGHTS — non validati. Mai esclusione, mai soglia minima
di ingresso in watchlist. Componenti mancanti → n/d nel breakdown e
rinormalizzazione sui pesi disponibili (niente zero punitivo su stock/senza futures).
"""
from __future__ import annotations

from config import CONFLUENCE_WEIGHTS, FUNDING_EXTREME, PLAYBOOK_THRESHOLDS, RVOL_INTEREST


def _score_tech(row: dict) -> float | None:
    """Situazione tecnica presente (watchlist = già setup). Bonus leggero se entry D."""
    if not row.get("setup"):
        return None
    # D leggermente sopra 4H-only: più contesto strutturale
    return 1.0 if row.get("entry_tf", "D") == "D" else 0.85


def _score_rs(row: dict) -> float | None:
    rs = row.get("rs_score")
    if rs is None:
        return None
    try:
        return float(max(0.0, min(1.0, rs)))
    except (TypeError, ValueError):
        return None


def _score_cvd_long(row: dict) -> float | None:
    st = row.get("cvd_state")
    if st is None:
        return None
    return {
        "up": 1.0,
        "flat": 0.55,
        "down": 0.25,
        "down_strong": 0.0,
    }.get(st, 0.55)


def _score_oi_expand(row: dict) -> float | None:
    st = row.get("oi_state")
    if st is None:
        return None
    return {
        "up": 1.0,
        "flat": 0.55,
        "down": 0.25,
        "collapse": 0.0,
    }.get(st, 0.55)


def _score_funding_ok(row: dict) -> float | None:
    """Per long: funding estremo positivo = carry avverso → basso."""
    if row.get("market") != "crypto":
        return None
    fr = row.get("funding")
    if fr is None:
        return None
    try:
        fr = float(fr)
    except (TypeError, ValueError):
        return None
    if fr >= FUNDING_EXTREME:
        return 0.0
    if fr >= FUNDING_EXTREME * 0.5:
        return 0.4
    if fr <= -FUNDING_EXTREME:
        return 0.85  # shorts pagano i long — non ideale ma non veto
    return 1.0


def _score_rvol(row: dict) -> float | None:
    rv = row.get("rvol")
    if rv is None:
        return None
    try:
        rv = float(rv)
    except (TypeError, ValueError):
        return None
    high = PLAYBOOK_THRESHOLDS.get("rvol", {}).get("high", RVOL_INTEREST)
    low = PLAYBOOK_THRESHOLDS.get("rvol", {}).get("low", 1.0)
    if rv >= high:
        return 1.0
    if rv >= low:
        return 0.55
    return 0.25


_COMPONENT_FNS = {
    "tech": _score_tech,
    "rs": _score_rs,
    "cvd_long": _score_cvd_long,
    "oi_expand": _score_oi_expand,
    "funding_ok": _score_funding_ok,
    "rvol": _score_rvol,
}


def confluence_score(row: dict, weights: dict | None = None) -> dict:
    """Ritorna {score: 0..100, breakdown: {comp: {weight, raw, contrib, status}}}.

    status = "ok" | "n/d". Score rinormalizzato solo sui pesi disponibili.
    """
    w = dict(weights or CONFLUENCE_WEIGHTS)
    breakdown: dict = {}
    available: list[tuple[str, float, float]] = []  # name, weight, raw 0..1

    for name, weight in w.items():
        fn = _COMPONENT_FNS.get(name)
        raw = fn(row) if fn else None
        if raw is None:
            breakdown[name] = {
                "weight": weight,
                "raw": None,
                "contrib": None,
                "status": "n/d",
            }
            continue
        available.append((name, weight, float(raw)))
        breakdown[name] = {
            "weight": weight,
            "raw": round(float(raw), 4),
            "contrib": None,  # fill after renorm
            "status": "ok",
        }

    if not available:
        return {"score": 0.0, "breakdown": breakdown, "renorm": True}

    wsum = sum(wt for _, wt, _ in available)
    score = 0.0
    for name, weight, raw in available:
        nw = weight / wsum
        contrib = nw * raw * 100.0
        breakdown[name]["contrib"] = round(contrib, 2)
        breakdown[name]["weight_norm"] = round(nw, 4)
        score += contrib

    return {
        "score": round(score, 1),
        "breakdown": breakdown,
        "renorm": len(available) < len(w),
    }


def attach_confluence(row: dict) -> dict:
    """Allega confluence_score + breakdown alla riga watchlist."""
    result = confluence_score(row)
    row["confluence"] = result["score"]
    row["confluence_breakdown"] = result["breakdown"]
    row["confluence_renorm"] = result["renorm"]
    return row


def sort_by_confluence(rows: list[dict]) -> list[dict]:
    """Ordina desc per confluence; tie-break RS. Non filtra."""
    for r in rows:
        if "confluence" not in r:
            attach_confluence(r)
    return sorted(
        rows,
        key=lambda r: (r.get("confluence") or 0.0, r.get("rs_score") or 0.0),
        reverse=True,
    )


__all__ = [
    "confluence_score",
    "attach_confluence",
    "sort_by_confluence",
]
