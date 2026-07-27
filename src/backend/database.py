"""SQLite: impostazioni, journal trades, alert.

Lo schema trades è versionato in modo conservativo: init_db() crea la tabella
base e migrate_trades_schema() aggiunge le colonne nuove se mancano (idempotente).
I record storici restano leggibili; i campi nuovi sono NULL.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone

from config import DB_PATH, DEFAULT_SETTINGS

_lock = threading.Lock()
_conn: sqlite3.Connection | None = None

# Colonne aggiunte dopo lo schema iniziale. Migrazione idempotente via ALTER TABLE.
# scenario_ids: JSON text (lista), anticipato per FASE 5-BIS playbook.
TRADE_OPTIONAL_COLUMNS: list[tuple[str, str]] = [
    ("timeframe", "TEXT"),                 # D | 4H | 1H | 15m
    ("pattern", "TEXT"),                   # pullback | compression | breakout | discrezionale
    ("oi_at_entry", "REAL"),
    ("cvd_slope_at_entry", "REAL"),
    ("funding_at_entry", "REAL"),
    ("rvol_at_entry", "REAL"),
    ("mae_r", "REAL"),
    ("mfe_r", "REAL"),
    ("note", "TEXT"),                      # nota breve opzionale (notes resta il campo storico)
    ("scenario_ids", "TEXT"),              # JSON list[str], valorizzato dal playbook
]


def conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
    return _conn


def init_db() -> None:
    with _lock:
        c = conn()
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS trades (
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
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                market TEXT NOT NULL,
                symbol TEXT NOT NULL,
                message TEXT NOT NULL,
                read INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        c.commit()
        _migrate_trades_schema_unlocked(c)


def migrate_trades_schema(connection: sqlite3.Connection | None = None) -> list[str]:
    """Aggiunge le colonne opzionali mancanti. Idempotente. Ritorna i nomi aggiunti."""
    if connection is not None:
        return _migrate_trades_schema_unlocked(connection)
    with _lock:
        return _migrate_trades_schema_unlocked(conn())


def _migrate_trades_schema_unlocked(c: sqlite3.Connection) -> list[str]:
    existing = {
        row[1]
        for row in c.execute("PRAGMA table_info(trades)").fetchall()
    }
    added: list[str] = []
    for name, col_type in TRADE_OPTIONAL_COLUMNS:
        if name in existing:
            continue
        c.execute(f"ALTER TABLE trades ADD COLUMN {name} {col_type}")
        added.append(name)
    if added:
        c.commit()
    return added


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------- Settings ----------

def get_settings() -> dict:
    with _lock:
        rows = conn().execute("SELECT key, value FROM settings").fetchall()
    stored = {r["key"]: json.loads(r["value"]) for r in rows}
    return {**DEFAULT_SETTINGS, **stored}


def update_settings(values: dict) -> dict:
    with _lock:
        c = conn()
        for key, val in values.items():
            if key in DEFAULT_SETTINGS:
                c.execute(
                    "INSERT INTO settings(key, value) VALUES(?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                    (key, json.dumps(val)),
                )
        c.commit()
    return get_settings()


# ---------- Trades ----------

_OPTIONAL_TRADE_KEYS = {name for name, _ in TRADE_OPTIONAL_COLUMNS}


def _normalize_trade_row(row: sqlite3.Row | dict) -> dict:
    d = dict(row)
    # scenario_ids: esponi sempre come lista (None/assente → [])
    raw = d.get("scenario_ids")
    if raw is None or raw == "":
        d["scenario_ids"] = []
    elif isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            d["scenario_ids"] = parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            d["scenario_ids"] = []
    return d


def list_trades() -> list[dict]:
    with _lock:
        rows = conn().execute("SELECT * FROM trades ORDER BY opened_at DESC, id DESC").fetchall()
    return [_normalize_trade_row(r) for r in rows]


def create_trade(t: dict) -> dict:
    cols = [
        "symbol", "market", "direction", "setup", "entry_price", "stop_price",
        "size", "risk_amount", "notes", "opened_at",
    ]
    vals = [
        t["symbol"], t["market"], t["direction"], t["setup"],
        t["entry_price"], t["stop_price"], t["size"], t["risk_amount"],
        t.get("notes", "") or t.get("note", "") or "",
        t.get("opened_at") or now_iso(),
    ]
    for key in _OPTIONAL_TRADE_KEYS:
        if key == "notes":
            continue
        if key not in t or t[key] is None:
            continue
        cols.append(key)
        val = t[key]
        if key == "scenario_ids":
            val = json.dumps(val) if not isinstance(val, str) else val
        if key == "note" and not t.get("notes"):
            # se arriva solo note, già coperto sopra; qui salva anche in note
            pass
        vals.append(val)

    placeholders = ",".join("?" * len(cols))
    col_sql = ",".join(cols)
    with _lock:
        c = conn()
        cur = c.execute(
            f"INSERT INTO trades({col_sql}) VALUES({placeholders})",
            tuple(vals),
        )
        c.commit()
        row = c.execute("SELECT * FROM trades WHERE id = ?", (cur.lastrowid,)).fetchone()
    return _normalize_trade_row(row)


def close_trade(
    trade_id: int,
    exit_price: float,
    mistake: bool,
    notes: str,
    *,
    mae_r: float | None = None,
    mfe_r: float | None = None,
) -> dict | None:
    with _lock:
        c = conn()
        row = c.execute("SELECT * FROM trades WHERE id = ?", (trade_id,)).fetchone()
        if row is None or row["status"] == "closed":
            return None
        risk_per_unit = abs(row["entry_price"] - row["stop_price"])
        if risk_per_unit <= 0:
            return None
        if row["direction"] == "long":
            r_result = (exit_price - row["entry_price"]) / risk_per_unit
        else:
            r_result = (row["entry_price"] - exit_price) / risk_per_unit
        merged_notes = (row["notes"] + "\n" + notes).strip() if notes else row["notes"]
        # mae/mfe: aggiorna solo se forniti (altrimenti restano NULL o valore precedente)
        sets = [
            "status='closed'", "exit_price=?", "r_result=?", "mistake=?",
            "notes=?", "closed_at=?",
        ]
        params: list = [exit_price, round(r_result, 3), int(mistake), merged_notes, now_iso()]
        if mae_r is not None:
            sets.append("mae_r=?")
            params.append(mae_r)
        if mfe_r is not None:
            sets.append("mfe_r=?")
            params.append(mfe_r)
        params.append(trade_id)
        c.execute(f"UPDATE trades SET {', '.join(sets)} WHERE id=?", params)
        c.commit()
        row = c.execute("SELECT * FROM trades WHERE id = ?", (trade_id,)).fetchone()
    return _normalize_trade_row(row)


def delete_trade(trade_id: int) -> bool:
    with _lock:
        c = conn()
        cur = c.execute("DELETE FROM trades WHERE id = ?", (trade_id,))
        c.commit()
    return cur.rowcount > 0


# ---------- Alerts ----------

def add_alert(market: str, symbol: str, message: str) -> dict:
    with _lock:
        c = conn()
        cur = c.execute(
            "INSERT INTO alerts(created_at, market, symbol, message) VALUES(?,?,?,?)",
            (now_iso(), market, symbol, message),
        )
        c.commit()
        row = c.execute("SELECT * FROM alerts WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)


def list_alerts(limit: int = 50) -> list[dict]:
    with _lock:
        rows = conn().execute(
            "SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def mark_alerts_read() -> None:
    with _lock:
        c = conn()
        c.execute("UPDATE alerts SET read = 1 WHERE read = 0")
        c.commit()
