import * as SQLite from "expo-sqlite";

import { DEFAULT_SETTINGS } from "../config";
import type { Alert, Settings, Trade } from "../engine/types";

let _db: SQLite.SQLiteDatabase | null = null;
let _initialized = false;

function db(): SQLite.SQLiteDatabase {
  if (!_db) {
    _db = SQLite.openDatabaseSync("vision_app.db");
  }
  if (!_initialized) {
    initDbSchema();
  }
  return _db;
}

function nowIso(): string {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "+00:00");
}

function initDbSchema(): void {
  if (_initialized) return;
  _db!.execSync(`
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
  `);
  _initialized = true;
}

/** Crea le tabelle se mancanti. Idempotente — sicuro chiamarla più volte. */
export function initDb(): void {
  if (!_db) {
    _db = SQLite.openDatabaseSync("vision_app.db");
  }
  initDbSchema();
}

export function isDbReady(): boolean {
  return _initialized;
}

export function getSettings(): Settings {
  const rows = db().getAllSync<{ key: string; value: string }>(
    "SELECT key, value FROM settings"
  );
  const stored: Partial<Settings> = {};
  for (const r of rows) {
    stored[r.key as keyof Settings] = JSON.parse(r.value);
  }
  return { ...DEFAULT_SETTINGS, ...stored };
}

export function updateSettings(values: Partial<Settings>): Settings {
  const database = db();
  for (const [key, val] of Object.entries(values)) {
    if (key in DEFAULT_SETTINGS) {
      database.runSync(
        "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        key,
        JSON.stringify(val)
      );
    }
  }
  return getSettings();
}

export function listTrades(): Trade[] {
  return db().getAllSync<Trade>(
    "SELECT * FROM trades ORDER BY opened_at DESC, id DESC"
  );
}

export function createTrade(t: Partial<Trade> & Pick<Trade, "symbol" | "market" | "direction" | "setup" | "entry_price" | "stop_price" | "size" | "risk_amount">): Trade {
  const openedAt = t.opened_at ?? nowIso();
  const result = db().runSync(
    `INSERT INTO trades(symbol, market, direction, setup, entry_price, stop_price,
                        size, risk_amount, notes, opened_at)
     VALUES(?,?,?,?,?,?,?,?,?,?)`,
    t.symbol,
    t.market,
    t.direction,
    t.setup,
    t.entry_price,
    t.stop_price,
    t.size,
    t.risk_amount,
    t.notes ?? "",
    openedAt
  );
  const row = db().getFirstSync<Trade>("SELECT * FROM trades WHERE id = ?", result.lastInsertRowId);
  if (!row) throw new Error("Trade non creato");
  return row;
}

export function closeTrade(
  tradeId: number,
  exitPrice: number,
  mistake: boolean,
  notes: string
): Trade | null {
  const row = db().getFirstSync<Trade>("SELECT * FROM trades WHERE id = ?", tradeId);
  if (!row || row.status === "closed") return null;

  const riskPerUnit = Math.abs(row.entry_price - row.stop_price);
  if (riskPerUnit <= 0) return null;

  const rResult =
    row.direction === "long"
      ? (exitPrice - row.entry_price) / riskPerUnit
      : (row.entry_price - exitPrice) / riskPerUnit;

  const mergedNotes = notes ? `${row.notes}\n${notes}`.trim() : row.notes;

  db().runSync(
    `UPDATE trades SET status='closed', exit_price=?, r_result=?, mistake=?,
                       notes=?, closed_at=? WHERE id=?`,
    exitPrice,
    Math.round(rResult * 1000) / 1000,
    mistake ? 1 : 0,
    mergedNotes,
    nowIso(),
    tradeId
  );

  return db().getFirstSync<Trade>("SELECT * FROM trades WHERE id = ?", tradeId) ?? null;
}

export function deleteTrade(tradeId: number): boolean {
  const result = db().runSync("DELETE FROM trades WHERE id = ?", tradeId);
  return result.changes > 0;
}

export function addAlert(market: string, symbol: string, message: string): Alert {
  const createdAt = nowIso();
  const result = db().runSync(
    "INSERT INTO alerts(created_at, market, symbol, message) VALUES(?,?,?,?)",
    createdAt,
    market,
    symbol,
    message
  );
  const row = db().getFirstSync<Alert>("SELECT * FROM alerts WHERE id = ?", result.lastInsertRowId);
  if (!row) throw new Error("Alert non creato");
  return row;
}

export function listAlerts(limit = 50): Alert[] {
  return db().getAllSync<Alert>(
    "SELECT * FROM alerts ORDER BY id DESC LIMIT ?",
    limit
  );
}

export function markAlertsRead(): void {
  db().runSync("UPDATE alerts SET read = 1 WHERE read = 0");
}

export function countUnreadAlerts(): number {
  const row = db().getFirstSync<{ c: number }>(
    "SELECT COUNT(*) as c FROM alerts WHERE read = 0"
  );
  return row?.c ?? 0;
}
