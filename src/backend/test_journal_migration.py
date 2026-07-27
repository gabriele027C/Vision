"""Test migrazione journal FASE 0: schema esteso, idempotenza, metriche breakdown."""
from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path

import database
import services.metrics as metrics_mod


def _fresh_db(tmp: Path):
    """Punta database.DB_PATH a un file temporaneo e reinizializza la connessione."""
    database._conn = None
    database.DB_PATH = tmp / "test_journal.db"  # type: ignore[attr-defined]
    # DB_PATH è importato da config: monkeypatch sul modulo database
    import config
    config.DB_PATH = tmp / "test_journal.db"
    database.DB_PATH = config.DB_PATH
    database._conn = None
    database.init_db()


def test_migration_adds_columns_idempotently(tmp_path, monkeypatch):
    db_file = tmp_path / "old.db"
    # Simula DB PRE-migrazione: solo colonne originali
    c = sqlite3.connect(db_file)
    c.executescript(
        """
        CREATE TABLE trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            market TEXT NOT NULL,
            direction TEXT NOT NULL,
            setup TEXT NOT NULL,
            entry_price REAL NOT NULL,
            stop_price REAL NOT NULL,
            size REAL NOT NULL,
            risk_amount REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            exit_price REAL,
            r_result REAL,
            mistake INTEGER NOT NULL DEFAULT 0,
            notes TEXT NOT NULL DEFAULT '',
            opened_at TEXT NOT NULL,
            closed_at TEXT
        );
        """
    )
    c.execute(
        """INSERT INTO trades(symbol, market, direction, setup, entry_price, stop_price,
           size, risk_amount, status, exit_price, r_result, mistake, notes, opened_at, closed_at)
           VALUES('BTCUSDT','crypto','long','A',100,95,1,50,'closed',110,2.0,0,'old',
           '2024-01-01T00:00:00','2024-01-02T00:00:00')"""
    )
    c.commit()
    c.close()

    monkeypatch.setattr(database, "DB_PATH", db_file)
    database._conn = None
    # Riapri e migra
    conn = database.conn()
    added = database.migrate_trades_schema(conn)
    assert "timeframe" in added
    assert "pattern" in added
    assert "scenario_ids" in added

    # Idempotenza: seconda chiamata non aggiunge nulla
    added2 = database.migrate_trades_schema(conn)
    assert added2 == []

    row = dict(conn.execute("SELECT * FROM trades WHERE id=1").fetchone())
    assert row["symbol"] == "BTCUSDT"
    assert row["r_result"] == 2.0
    assert row["timeframe"] is None
    assert row["pattern"] is None
    assert row["rvol_at_entry"] is None


def test_create_new_trade_with_extended_fields(tmp_path, monkeypatch):
    db_file = tmp_path / "new.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)
    database._conn = None
    database.init_db()

    t = database.create_trade({
        "symbol": "ETHUSDT",
        "market": "crypto",
        "direction": "long",
        "setup": "B",
        "entry_price": 2000.0,
        "stop_price": 1900.0,
        "size": 0.5,
        "risk_amount": 50.0,
        "notes": "nuovo",
        "timeframe": "4H",
        "pattern": "compression",
        "rvol_at_entry": 1.8,
        "funding_at_entry": 0.0001,
        "oi_at_entry": 0.08,
        "cvd_slope_at_entry": 0.2,
        "scenario_ids": ["trend_nuovi_aggressori"],
    })
    assert t["timeframe"] == "4H"
    assert t["pattern"] == "compression"
    assert t["rvol_at_entry"] == 1.8
    assert t["scenario_ids"] == ["trend_nuovi_aggressori"]

    # Vecchio trade senza campi nuovi resta visibile
    old = database.create_trade({
        "symbol": "BTCUSDT",
        "market": "crypto",
        "direction": "long",
        "setup": "A",
        "entry_price": 100.0,
        "stop_price": 95.0,
        "size": 1.0,
        "risk_amount": 5.0,
    })
    assert old["timeframe"] is None
    assert old["scenario_ids"] == []

    all_t = database.list_trades()
    assert len(all_t) == 2


def test_metrics_breakdown_and_random_benchmark(tmp_path, monkeypatch):
    db_file = tmp_path / "met.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)
    database._conn = None
    database.init_db()

    # 3 chiusi: 1 win 2R, 2 loss -1R → WR 33.3%, exp 0
    specs = [
        ("D", "pullback", 1.2, 2.0),
        ("D", "compression", 0.8, -1.0),
        ("4H", "breakout", 1.8, -1.0),
    ]
    for i, (tf, pat, rvol, r) in enumerate(specs):
        t = database.create_trade({
            "symbol": f"S{i}",
            "market": "crypto",
            "direction": "long",
            "setup": "A",
            "entry_price": 100.0,
            "stop_price": 95.0,
            "size": 1.0,
            "risk_amount": 5.0,
            "timeframe": tf,
            "pattern": pat,
            "rvol_at_entry": rvol,
            "scenario_ids": ["short_covering"] if i == 0 else [],
        })
        exit_px = 100.0 + r * 5.0  # risk_per_unit=5
        database.close_trade(t["id"], exit_px, False, "")

    m = metrics_mod.compute_metrics()
    assert m["closed_trades"] == 3
    assert m["win_rate"] == 33.3
    assert abs(m["expectancy"]) < 0.01
    assert m["random_benchmark"]["expected_wr_pct"] == 33.3
    assert m["random_benchmark"]["delta_wr_pp"] == 0.0

    tfs = {x["key"]: x for x in m["by_timeframe"]}
    assert tfs["D"]["n"] == 2
    assert tfs["4H"]["n"] == 1

    pats = {x["key"]: x for x in m["by_pattern"]}
    assert "pullback" in pats and "compression" in pats and "breakout" in pats

    assert any(b["key"] == "1.0-1.5" for b in m["by_context"]["rvol"])
    # scenario con n<10 non compare
    assert m["by_scenario"] == []


def test_old_and_new_records_both_in_aggregates(tmp_path, monkeypatch):
    db_file = tmp_path / "mix.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)
    database._conn = None
    database.init_db()

    old = database.create_trade({
        "symbol": "OLD", "market": "crypto", "direction": "long", "setup": "A",
        "entry_price": 100, "stop_price": 90, "size": 1, "risk_amount": 10,
    })
    database.close_trade(old["id"], 120, False, "")  # +2R

    new = database.create_trade({
        "symbol": "NEW", "market": "crypto", "direction": "long", "setup": "B",
        "entry_price": 100, "stop_price": 90, "size": 1, "risk_amount": 10,
        "timeframe": "1H", "pattern": "discrezionale",
    })
    database.close_trade(new["id"], 90, False, "", mae_r=1.0, mfe_r=0.5)  # -1R

    m = metrics_mod.compute_metrics()
    assert m["closed_trades"] == 2
    assert m["expectancy"] == 0.5  # (2 + -1) / 2
    # solo il nuovo ha timeframe
    assert m["by_timeframe"][0]["key"] == "1H"
    assert m["by_timeframe"][0]["n"] == 1

    closed_new = [t for t in database.list_trades() if t["symbol"] == "NEW"][0]
    assert closed_new["mae_r"] == 1.0
    assert closed_new["mfe_r"] == 0.5
