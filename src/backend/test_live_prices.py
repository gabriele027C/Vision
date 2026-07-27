"""Test coerenza prezzo/status e refresh live."""
from services.live_prices import apply_live_prices, reconcile_status_with_price


def test_triggered_long_below_trigger_downgrades():
    row = {
        "direction": "long",
        "status": "triggered",
        "last_price": 244.39,
        "entry_trigger": 252.26,
        "warnings": [],
    }
    reconcile_status_with_price(row)
    assert row["status"] == "watch"  # 244 < 0.99*252
    assert any("riallineato" in w for w in row["warnings"])


def test_triggered_long_near_band_becomes_near():
    row = {
        "direction": "long",
        "status": "triggered",
        "last_price": 251.0,
        "entry_trigger": 252.0,
        "warnings": [],
    }
    reconcile_status_with_price(row)
    assert row["status"] == "near"


def test_triggered_stays_if_price_above():
    row = {
        "direction": "long",
        "status": "triggered",
        "last_price": 260.0,
        "entry_trigger": 252.0,
        "warnings": [],
    }
    reconcile_status_with_price(row)
    assert row["status"] == "triggered"


def test_blocked_untouched():
    row = {
        "direction": "long",
        "status": "blocked",
        "last_price": 100.0,
        "entry_trigger": 200.0,
        "warnings": [],
    }
    reconcile_status_with_price(row)
    assert row["status"] == "blocked"


def test_apply_live_prices_sets_flags():
    rows = [
        {
            "symbol": "DDOG",
            "direction": "long",
            "status": "triggered",
            "last_price": 244.0,
            "entry_trigger": 252.0,
            "warnings": [],
        }
    ]
    n = apply_live_prices(rows, {"DDOG": 255.5})
    assert n == 1
    assert rows[0]["last_price"] == 255.5
    assert rows[0]["price_live"] is True
    assert rows[0]["status"] == "triggered"
