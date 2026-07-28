"""Position sizing frazionale fisso (§7) con vincoli futures.

size = rischio in valuta / distanza dallo stop, poi:
- cap di leva (crypto 5x default, stocks 2x Reg-T);
- per crypto: prezzo di liquidazione approssimato e verifica che lo stop
  scatti PRIMA della liquidazione (altrimenti errore bloccante);
- costi round-trip taker (+ funding stimato opzionale) e target 2R al netto.

Liquidazione e rischio 1% / cap 5x
---------------------------------
Con rischio tipico (~1%) e CRYPTO_MAX_LEVERAGE=5x, uno stop “oltre la
liquidazione” è irraggiungibile: il cap di leva sposta la liq abbastanza
lontano che stop realistici restano sempre “safe”. Non è un bug.
Anche a risk_pct=5% con max_leverage=20, uno stop abbastanza stretto da
implicare 20x resta sopra la liq a 20x — il blocco richiede parametri
veramente anomali (es. risk_pct molto alto + max_leverage elevato).

Il check `liq_safe` è una rete di sicurezza se i parametri cambiano
(max_leverage più alto, risk_pct anomalo, stop molto lontano). In quel caso
ritorna errore bloccante con liq_safe=False. I client devono anche disabilitare
esplicitamente il bottone di registrazione su liq_safe===false / sizingError,
non affidarsi solo all’HTTP 400.

La firma resta retrocompatibile: i vecchi chiamanti
position_size(capital, risk_pct, entry, stop, half_size) continuano a
funzionare (direction viene inferita dalla posizione dello stop).
"""

CRYPTO_MAX_LEVERAGE = 5.0
STOCKS_MAX_LEVERAGE = 2.0  # margine Reg-T
DEFAULT_TAKER_FEE = 0.00055  # 0.055% per lato (taker Bybit/Binance futures)
DEFAULT_FUNDING_DAILY = 0.0003  # stima 0.01%/8h * 3


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
    funding_est: float | None = None,
    days_held_est: float = 0.0,
) -> dict:
    """Calcola size, leva, liquidazione e costi.

    funding_est: tasso funding giornaliero stimato (frazione). Se None e market
    crypto, usa DEFAULT_FUNDING_DAILY. days_held_est: giorni stimati in posizione
    per il costo funding (0 = solo fee taker round-trip).
    """
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
        notional = max_leverage * capital
        size_units = notional / entry
        risk_amount = size_units * distance

    leverage = notional / capital if capital > 0 else 0.0

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

    fee_rt = 2.0 * taker_fee * notional
    if funding_est is None:
        funding_est = DEFAULT_FUNDING_DAILY if market == "crypto" else 0.0
    funding_cost = abs(funding_est) * notional * max(days_held_est, 0.0)
    round_trip_cost = fee_rt + funding_cost
    cost_r = round_trip_cost / risk_amount if risk_amount > 0 else 0.0
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
        "taker_fee": taker_fee,
        "funding_est": funding_est,
        "days_held_est": days_held_est,
        "fee_round_trip": round(fee_rt, 4),
        "funding_cost_est": round(funding_cost, 4),
        "round_trip_cost": round(round_trip_cost, 4),
        "cost_r": round(cost_r, 4),
        # Prezzo necessario perché il trade renda 2R DOPO i costi round-trip.
        "target_2r_net_long": round(entry + 2 * distance + cost_per_unit, 6),
        "target_2r_net_short": round(entry - 2 * distance - cost_per_unit, 6),
        "net_2r_after_costs": round(2.0 - cost_r, 4),
    }
