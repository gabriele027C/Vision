"""Test playbook: validazione JSON, trigger AND/OR, chiave mancante, famiglie."""
from engine.playbook import (
    active_scenarios,
    build_asset_state,
    load_playbook,
    primary_alert_scenario,
)


def test_load_playbook_valid():
    pb = load_playbook(force=True)
    assert len(pb["scenari"]) == 19
    assert "pre_ingresso" in pb["checklist_universali"]


def test_and_or_trigger_trend_nuovi_aggressori():
    state = {"prezzo": "up", "oi": "up", "cvd": "up"}
    ids = [c["id"] for c in active_scenarios(state)]
    assert "trend_nuovi_aggressori" in ids


def test_or_list_cvd_trend_senza_aggressori():
    # trigger: prezzo up, oi flat, cvd in [flat, down]
    state = {"prezzo": "up", "oi": "flat", "cvd": "down"}
    ids = [c["id"] for c in active_scenarios(state)]
    assert "trend_senza_aggressori" in ids


def test_missing_key_disables_card():
    # senza oi non si attiva short_covering (prezzo up + oi down)
    state = {"prezzo": "up"}
    ids = [c["id"] for c in active_scenarios(state)]
    assert "short_covering" not in ids
    state2 = {"prezzo": "up", "oi": "down"}
    assert "short_covering" in [c["id"] for c in active_scenarios(state2)]


def test_protections_sorted_first():
    state = {
        "prezzo": "up",
        "oi": "up",
        "cvd": "up",
        "funding": "extreme_against_long",
    }
    cards = active_scenarios(state)
    # carry_avverso (protezione) prima di trend_nuovi se entrambi matchano
    op_idx = next(i for i, c in enumerate(cards) if c["id"] == "trend_nuovi_aggressori")
    prot = [i for i, c in enumerate(cards) if not c["lato_operativo"]]
    if prot:
        assert min(prot) < op_idx or cards[0]["lato_operativo"] is False


def test_primary_alert_skips_protection():
    row = {
        "direction": "long",
        "funding": 0.001,  # extreme
        "setup": "A",
        "rvol": 1.2,
        "oi_state": "up",
        "cvd_state": "up",
        "price_state": "up",
    }
    # build via asset state manually
    from engine.playbook import build_asset_state, primary_alert_scenario

    flow = {"price_state": "up", "oi_state": "up", "cvd_state": "up"}
    card = primary_alert_scenario(row, flow)
    assert card is None or card.get("lato_operativo") is True


def test_family_coverage_at_least_one_each():
    pb = load_playbook()
    families = {c["famiglia"] for c in pb["scenari"]}
    assert families >= {"A", "B", "C", "D", "E", "F"}


def test_build_asset_state_from_row():
    row = {
        "direction": "long",
        "funding": -0.0001,
        "rvol": 2.0,
        "setup": "B",
        "oi_state": "flat",
        "cvd_state": "up",
        "tf_4h": {"squeeze": True},
    }
    st = build_asset_state(row, flow={"price_state": "up"})
    assert st["prezzo"] == "up"
    assert st["oi"] == "flat"
    assert st["cvd"] == "up"
    assert st["evento"] == "breakout"
    assert st["rvol"] == "high"
    assert st.get("squeeze_d_or_4h") is True
