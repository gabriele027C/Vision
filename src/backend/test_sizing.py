"""Unit test sizing con leva, liquidazione e costi — nessuna rete."""
from engine.sizing import (
    CRYPTO_MAX_LEVERAGE,
    STOCKS_MAX_LEVERAGE,
    position_size,
)


# ---------- Retrocompatibilità ----------


def test_backward_compatible_call():
    r = position_size(4000, 1.0, 100.0, 95.0, False)
    assert "error" not in r
    # Vecchie chiavi ancora presenti
    for key in (
        "risk_amount", "stop_distance", "stop_distance_pct", "size_units",
        "notional", "half_size", "target_2r_long", "target_2r_short",
    ):
        assert key in r
    assert r["risk_amount"] == 40.0
    assert r["size_units"] == 8.0
    assert r["direction"] == "long"  # inferita: stop < entry


def test_direction_inferred_short():
    r = position_size(4000, 1.0, 100.0, 105.0)
    assert r["direction"] == "short"


def test_invalid_distance_still_errors():
    r = position_size(4000, 1.0, 100.0, 100.0)
    assert "error" in r


# ---------- Cap di leva ----------


def test_implied_leverage_20x_capped_to_5x():
    # risk 20$ su distanza 0.1 → 200 unità → notional 20.000 su capitale 1.000 = 20x
    r = position_size(1000, 2.0, 100.0, 99.9, market="crypto")
    assert r["leverage_capped"] is True
    assert r["leverage"] == CRYPTO_MAX_LEVERAGE
    assert r["notional"] == 5000.0
    assert r["size_units"] == 50.0
    # Il rischio effettivo scende con la size cappata (50 unità * 0.1)
    assert r["risk_amount"] == 5.0


def test_leverage_not_capped_below_limit():
    r = position_size(4000, 1.0, 100.0, 95.0, market="crypto")
    assert r["leverage_capped"] is False
    assert r["leverage"] < CRYPTO_MAX_LEVERAGE


def test_stocks_leverage_cap_reg_t():
    # 10x implicita su stocks → cap a 2x (Reg-T)
    r = position_size(1000, 1.0, 100.0, 99.9, market="stocks")
    assert r["leverage_capped"] is True
    assert r["leverage"] == STOCKS_MAX_LEVERAGE
    assert r["max_leverage"] == STOCKS_MAX_LEVERAGE
    # Niente liquidazione per stocks
    assert r["liq_price"] is None
    assert r["liq_safe"] is True


def test_custom_max_leverage_respected():
    r = position_size(1000, 2.0, 100.0, 99.9, max_leverage=3.0, market="crypto")
    assert r["leverage"] == 3.0
    assert r["leverage_capped"] is True


# ---------- Liquidazione (solo crypto) ----------


def test_stop_beyond_liquidation_long_is_blocking_error():
    # Cap a 5x → liq long = 100*(1 - 1/5) = 80. Stop a 75 < 80 → liquidazione
    # scatta PRIMA dello stop → errore bloccante, non warning.
    r = position_size(1000, 150.0, 100.0, 75.0, market="crypto")
    assert "error" in r
    assert r["liq_safe"] is False
    assert "liquidazione" in r["error"].lower()
    assert r["liq_price"] == 80.0


def test_stop_beyond_liquidation_short_is_blocking_error():
    # Short 5x → liq = 100*(1 + 1/5) = 120. Stop a 125 > 120 → errore.
    r = position_size(1000, 150.0, 100.0, 125.0, direction="short", market="crypto")
    assert "error" in r
    assert r["liq_safe"] is False


def test_stop_inside_liquidation_is_safe():
    # 5x cappata: liq long = 80, stop 99.9 > 80 → ok
    r = position_size(1000, 2.0, 100.0, 99.9, market="crypto")
    assert "error" not in r
    assert r["liq_safe"] is True
    assert r["liq_price"] == 80.0


def test_low_leverage_always_liq_safe():
    # Leva < 1: liq long negativa, mai raggiungibile
    r = position_size(10000, 1.0, 100.0, 90.0, market="crypto")
    assert r["liq_safe"] is True
    assert r["leverage"] < 1.0


def test_liq_block_with_anomalous_params_max_lev_20():
    """Rete di sicurezza: con max_leverage=20 e rischio anomalo lo stop lontano blocca.

    Nota: a risk_pct=5% il blocco resta matematicamente impossibile (per raggiungere
    20x lo stop deve essere così stretto da restare sopra la liq a 20x). Serve un
    risk_pct anomalo (qui 150%) insieme a max_leverage elevato.
    """
    r = position_size(
        1000, 150.0, 100.0, 75.0, market="crypto", max_leverage=20.0, direction="long"
    )
    assert "error" in r
    assert r["liq_safe"] is False
    assert r["leverage"] > 5.0  # sopra il default: la rete di sicurezza è attiva
    assert "liquidazione" in r["error"].lower()


def test_liq_block_does_not_fire_on_normal_1pct_5x():
    """Con rischio 1% e cap 5x default, anche stop ampi restano liq_safe."""
    # Spec audit: capital 4000, entry 100, stop 99 → leva ~1x, safe
    a = position_size(4000, 1.0, 100.0, 99.0, market="crypto")
    assert "error" not in a
    assert a["liq_safe"] is True
    assert a["leverage_capped"] is False
    # risk 5% + max_leverage 20 con stop ampio: leva bassa → non blocca
    b = position_size(1000, 5.0, 100.0, 75.0, market="crypto", max_leverage=20.0)
    assert "error" not in b
    assert b["liq_safe"] is True
    # Caso normale cappato a 5x
    c = position_size(1000, 1.0, 100.0, 75.0, market="crypto", max_leverage=5.0)
    assert "error" not in c
    assert c["liq_safe"] is True


# ---------- Costi ----------


def test_round_trip_cost_and_net_target():
    r = position_size(4000, 1.0, 100.0, 95.0, market="crypto")
    # cost = 2 * 0.00055 * notional
    assert r["round_trip_cost"] == round(2 * 0.00055 * r["notional"], 4)
    # Il target netto long è PIÙ LONTANO del lordo (serve coprire i costi)
    assert r["target_2r_net_long"] > r["target_2r_long"]
    # Il target netto short è più basso del lordo
    assert r["target_2r_net_short"] < r["target_2r_short"]
    # Delta = costo per unità
    cost_per_unit = r["round_trip_cost"] / r["size_units"]
    assert abs((r["target_2r_net_long"] - r["target_2r_long"]) - cost_per_unit) < 1e-6


def test_zero_fee_net_equals_gross():
    r = position_size(4000, 1.0, 100.0, 95.0, taker_fee=0.0)
    assert r["round_trip_cost"] == 0.0
    assert r["target_2r_net_long"] == r["target_2r_long"]
    assert r["target_2r_net_short"] == r["target_2r_short"]


def test_costs_reduce_net_2r():
    r = position_size(4000, 1.0, 100.0, 95.0, market="crypto", days_held_est=3)
    assert "error" not in r
    assert r["cost_r"] > 0
    assert r["net_2r_after_costs"] < 2.0
    assert r["net_2r_after_costs"] == round(2.0 - r["cost_r"], 4)
    assert r["funding_cost_est"] > 0
    assert r["round_trip_cost"] == round(r["fee_round_trip"] + r["funding_cost_est"], 4)


def test_half_size_halves_risk():
    full = position_size(4000, 1.0, 100.0, 95.0, False)
    half = position_size(4000, 1.0, 100.0, 95.0, True)
    assert half["risk_amount"] == full["risk_amount"] / 2
    assert half["size_units"] == full["size_units"] / 2
