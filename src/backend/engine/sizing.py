"""Position sizing frazionale fisso (§7): size = rischio in valuta / distanza dallo stop."""


def position_size(
    capital: float,
    risk_pct: float,
    entry: float,
    stop: float,
    half_size: bool = False,
) -> dict:
    risk_amount = capital * (risk_pct / 100.0)
    if half_size:
        risk_amount /= 2.0
    distance = abs(entry - stop)
    if distance <= 0 or entry <= 0:
        return {"error": "Entrata e stop non validi (distanza nulla)"}
    size_units = risk_amount / distance
    notional = size_units * entry
    return {
        "risk_amount": round(risk_amount, 2),
        "stop_distance": round(distance, 6),
        "stop_distance_pct": round(distance / entry * 100, 2),
        "size_units": round(size_units, 6),
        "notional": round(notional, 2),
        "half_size": half_size,
        "target_2r_long": round(entry + 2 * distance, 6),
        "target_2r_short": round(entry - 2 * distance, 6),
    }
