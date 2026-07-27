"""Parità Py↔TS: stessi asset_state sintetici → stessi scenario id."""
from engine.playbook import active_scenarios, load_playbook

# Vettori di stato usati anche da vision-mobile/src/engine/playbookParity.ts
PARITY_STATES = [
    {"prezzo": "up", "oi": "up", "cvd": "up"},
    {"prezzo": "up", "oi": "down"},
    {"prezzo": "up", "oi": "flat", "cvd": "down"},
    {"funding": "extreme_against_long"},
    {"funding": "negative", "prezzo": "up"},
    {"evento": "breakout", "rvol": "high"},
    {"squeeze_d_or_4h": True, "squeeze_1h_or_15m": True},
    {"trend": "down_aligned"},
    {"evento": "cascade", "oi": "collapse", "volume": "extreme"},
    {"prezzo": "up"},  # chiave mancante → niente short_covering
]


def ids_for(state: dict) -> list[str]:
    return [c["id"] for c in active_scenarios(state)]


def test_parity_vectors_nonempty_and_stable():
    load_playbook(force=True)
    results = [ids_for(s) for s in PARITY_STATES]
    # almeno alcuni stati attivano schede
    assert any(results)
    assert "trend_nuovi_aggressori" in results[0]
    assert "short_covering" in results[1]
    assert "carry_avverso" in results[3]
    assert "contesto_ribassista" in results[7]
    assert "capitolazione" in results[8]
    assert "short_covering" not in results[9]


def test_card_texts_not_truncated_in_payload():
    """Il rendering riceve testi completi dal JSON (nessun truncate lato motore)."""
    cards = active_scenarios({"prezzo": "up", "oi": "up", "cvd": "up"})
    card = next(c for c in cards if c["id"] == "trend_nuovi_aggressori")
    assert len(card["lettura"]) > 40
    assert len(card["footer"]) > 20
    assert len(card["monitorare"]) >= 2
