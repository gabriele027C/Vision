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


def test_stamp_live_prices_crypto(monkeypatch):
    from services import live_prices

    rows = [
        {
            "symbol": "BTCUSDT",
            "direction": "long",
            "status": "watch",
            "last_price": 60000.0,
            "entry_trigger": 65000.0,
            "warnings": [],
        }
    ]

    def fake_fetch(crypto_syms, stock_syms):
        assert crypto_syms == ["BTCUSDT"]
        assert stock_syms == []
        return {"BTCUSDT": 67432.1}

    monkeypatch.setattr(live_prices, "fetch_live_prices", fake_fetch)
    n = live_prices.stamp_live_prices(rows, "crypto")
    assert n == 1
    assert rows[0]["last_price"] == 67432.1
    assert rows[0]["price_live"] is True


def test_stamp_live_prices_stocks(monkeypatch):
    from services import live_prices

    rows = [
        {
            "symbol": "DDOG",
            "direction": "long",
            "status": "triggered",
            "last_price": 244.39,
            "entry_trigger": 252.26,
            "warnings": [],
        }
    ]

    def fake_fetch(crypto_syms, stock_syms):
        assert crypto_syms == []
        assert stock_syms == ["DDOG"]
        return {"DDOG": 248.0}

    monkeypatch.setattr(live_prices, "fetch_live_prices", fake_fetch)
    n = live_prices.stamp_live_prices(rows, "stocks")
    assert n == 1
    assert rows[0]["last_price"] == 248.0
    assert rows[0]["status"] == "watch"  # live sotto trigger → riallinea
