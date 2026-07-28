"""Registrazione trade da Planner: snapshot OI/CVD at-entry persistiti nel DB."""
from __future__ import annotations

from pathlib import Path

import config
import database


def _fresh_db(tmp: Path):
    database._conn = None
    config.DB_PATH = tmp / "planner_flow.db"
    database.DB_PATH = config.DB_PATH
    database._conn = None
    database.init_db()


def test_create_trade_persists_oi_cvd_from_watchlist_snapshot(tmp_path):
    """Simula registerTrade del Planner con campi prefillati da riga watchlist."""
    _fresh_db(tmp_path)

    watch_row = {
        "symbol": "BTCUSDT",
        "market": "crypto",
        "oi_delta_24h": 0.042,
        "cvd_slope": 0.031,
        "funding": 0.0001,
        "rvol": 1.7,
        "scenario_ids": ["long_oi_cvd_confirm"],
    }

    created = database.create_trade(
        {
            "symbol": watch_row["symbol"],
            "market": watch_row["market"],
            "direction": "long",
            "setup": "A",
            "entry_price": 65000.0,
            "stop_price": 64000.0,
            "size": 0.01,
            "risk_amount": 40.0,
            "notes": "Pianificato dal Planner (test)",
            "timeframe": "D",
            "pattern": "pullback",
            "oi_at_entry": watch_row["oi_delta_24h"],
            "cvd_slope_at_entry": watch_row["cvd_slope"],
            "funding_at_entry": watch_row["funding"],
            "rvol_at_entry": watch_row["rvol"],
            "scenario_ids": watch_row["scenario_ids"],
        }
    )

    assert created["id"] >= 1
    loaded = next(t for t in database.list_trades() if t["id"] == created["id"])

    assert loaded["oi_at_entry"] == 0.042
    assert loaded["cvd_slope_at_entry"] == 0.031
    assert loaded["funding_at_entry"] == 0.0001
    assert loaded["rvol_at_entry"] == 1.7
    assert loaded["timeframe"] == "D"
    assert loaded["pattern"] == "pullback"
    ids = loaded.get("scenario_ids")
    if isinstance(ids, str):
        import json

        ids = json.loads(ids)
    assert "long_oi_cvd_confirm" in (ids or [])
