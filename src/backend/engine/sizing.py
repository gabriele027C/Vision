"""Position sizing frazionale fisso (§7) con vincoli futures.

size = rischio in valuta / distanza dallo stop, poi:
- cap di leva (crypto 5x default, stocks 2x Reg-T);
- per crypto: prezzo di liquidazione approssimato e verifica che lo stop
  scatti PRIMA della liquidazione (altrimenti errore bloccante);
- costi round-trip taker e target 2R al netto dei costi.

La firma resta retrocompatibile: i vecchi chiamanti
position_size(capital, risk_pct, entry, stop, half_size) continuano a
funzionare (direction viene inferita dalla posizione dello stop).
"""

CRYPTO_MAX_LEVERAGE = 5.0
STOCKS_MAX_LEVERAGE = 2.0  # margine Reg-T
DEFAULT_TAKER_FEE = 0.00055  # 0.055% per lato (taker Bybit/Binance futures)


def position_size(
    capital: float,
    risk_pct: float,
    entry: float,
    stop: float,
    half_size: bool = False,
    direction: str | None = None,
    max_leverage: float | None = None,
    taker_fee: float = DEFAULT_TAKER_FEE,
    market: str = "crypto",
) -> dict:
    risk_amount = capital * (risk_pct / 100.0)
    if half_size:
        risk_amount /= 2.0
    distance = abs(entry - stop)
    if distance <= 0 or entry <= 0:
        return {"error": "Entrata e stop non validi (distanza nulla)"}

    if direction is None:
        direction = "long" if stop < entry else "short"

    if max_leverage is None:
        max_leverage = STOCKS_MAX_LEVERAGE if market == "stocks" else CRYPTO_MAX_LEVERAGE

    size_units = risk_amount / distance
    notional = size_units * entry
    implied_leverage = notional / capital if capital > 0 else 0.0

    leverage_capped = implied_leverage > max_leverage
    if leverage_capped:
        # Cap del notional: la size scende e con lei il rischio effettivo.
        notional = max_leverage * capital
        size_units = notional / entry
        risk_amount = size_units * distance

    leverage = notional / capital if capital > 0 else 0.0

    # Liquidazione approssimata (cross ~ isolata senza maintenance margin):
    # long liq = entry*(1 - 1/lev); short liq = entry*(1 + 1/lev).
    # Con leva <= 1 il prezzo di liquidazione long è <= 0: mai raggiungibile.
    liq_price: float | None = None
    liq_safe = True
    if market == "crypto" and leverage > 0:
        if direction == "long":
            liq_price = entry * (1.0 - 1.0 / leverage)
            liq_safe = stop > liq_price
        else:
            liq_price = entry * (1.0 + 1.0 / leverage)
            liq_safe = stop < liq_price
        if not liq_safe:
            return {
                "error": (
                    f"Stop ({stop:g}) oltre il prezzo di liquidazione stimato "
                    f"({liq_price:.6g}) a leva {leverage:.2f}x: la posizione verrebbe "
                    f"liquidata prima dello stop. Riduci la leva o avvicina lo stop."
                ),
                "liq_price": round(liq_price, 6),
                "leverage": round(leverage, 2),
                "liq_safe": False,
            }

    round_trip_cost = 2.0 * taker_fee * notional
    cost_per_unit = round_trip_cost / size_units if size_units > 0 else 0.0

    return {
        "risk_amount": round(risk_amount, 2),
        "stop_distance": round(distance, 6),
        "stop_distance_pct": round(distance / entry * 100, 2),
        "size_units": round(size_units, 6),
        "notional": round(notional, 2),
        "half_size": half_size,
        "target_2r_long": round(entry + 2 * distance, 6),
        "target_2r_short": round(entry - 2 * distance, 6),
        "direction": direction,
        "market": market,
        "leverage": round(leverage, 2),
        "max_leverage": max_leverage,
        "leverage_capped": leverage_capped,
        "liq_price": round(liq_price, 6) if liq_price is not None else None,
        "liq_safe": liq_safe,
        "round_trip_cost": round(round_trip_cost, 4),
        # Prezzo necessario perché il trade renda 2R DOPO i costi round-trip.
        "target_2r_net_long": round(entry + 2 * distance + cost_per_unit, 6),
        "target_2r_net_short": round(entry - 2 * distance - cost_per_unit, 6),
    }
