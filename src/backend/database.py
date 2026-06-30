"""SQLite: impostazioni, journal trades, alert."""
import json
import sqlite3
import threading
from datetime import datetime, timezone

from config import DB_PATH, DEFAULT_SETTINGS

_lock = threading.Lock()
_conn: sqlite3.Connection | None = None


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

def list_trades() -> list[dict]:
    with _lock:
        rows = conn().execute("SELECT * FROM trades ORDER BY opened_at DESC, id DESC").fetchall()
    return [dict(r) for r in rows]


def create_trade(t: dict) -> dict:
    with _lock:
        c = conn()
        cur = c.execute(
            """INSERT INTO trades(symbol, market, direction, setup, entry_price, stop_price,
                                  size, risk_amount, notes, opened_at)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (
                t["symbol"], t["market"], t["direction"], t["setup"],
                t["entry_price"], t["stop_price"], t["size"], t["risk_amount"],
                t.get("notes", ""), t.get("opened_at") or now_iso(),
            ),
        )
        c.commit()
        row = c.execute("SELECT * FROM trades WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)


def close_trade(trade_id: int, exit_price: float, mistake: bool, notes: str) -> dict | None:
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
        c.execute(
            """UPDATE trades SET status='closed', exit_price=?, r_result=?, mistake=?,
                                 notes=?, closed_at=? WHERE id=?""",
            (exit_price, round(r_result, 3), int(mistake), merged_notes, now_iso(), trade_id),
        )
        c.commit()
        row = c.execute("SELECT * FROM trades WHERE id = ?", (trade_id,)).fetchone()
    return dict(row)


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
