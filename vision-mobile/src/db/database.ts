import * as SQLite from "expo-sqlite";

import { DEFAULT_SETTINGS } from "../config";
import type { Alert, Settings, Trade } from "../engine/types";

let _db: SQLite.SQLiteDatabase | null = null;
let _initialized = false;

/** Colonne FASE 0 — migrazione idempotente via ALTER TABLE. */
export const TRADE_OPTIONAL_COLUMNS: { name: string; type: string }[] = [
  { name: "timeframe", type: "TEXT" },
  { name: "pattern", type: "TEXT" },
  { name: "oi_at_entry", type: "REAL" },
  { name: "cvd_slope_at_entry", type: "REAL" },
  { name: "funding_at_entry", type: "REAL" },
  { name: "rvol_at_entry", type: "REAL" },
  { name: "mae_r", type: "REAL" },
  { name: "mfe_r", type: "REAL" },
  { name: "note", type: "TEXT" },
  { name: "scenario_ids", type: "TEXT" },
];

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

function migrateTradesSchemaUnlocked(): string[] {
  const rows = _db!.getAllSync<{ name: string }>("PRAGMA table_info(trades)");
  const existing = new Set(rows.map((r) => r.name));
  const added: string[] = [];
  for (const col of TRADE_OPTIONAL_COLUMNS) {
    if (existing.has(col.name)) continue;
    _db!.execSync(`ALTER TABLE trades ADD COLUMN ${col.name} ${col.type}`);
    added.push(col.name);
  }
  return added;
}

/** Aggiunge colonne opzionali mancanti. Idempotente. */
export function migrateTradesSchema(): string[] {
  db();
  return migrateTradesSchemaUnlocked();
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
  migrateTradesSchemaUnlocked();
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

function normalizeTradeRow(row: Trade & { scenario_ids?: string | string[] | null }): Trade {
  const raw = row.scenario_ids;
  let scenarioIds: string[] = [];
  if (raw == null || raw === "") {
    scenarioIds = [];
  } else if (Array.isArray(raw)) {
    scenarioIds = raw;
  } else if (typeof raw === "string") {
    try {
      const parsed = JSON.parse(raw);
      scenarioIds = Array.isArray(parsed) ? parsed : [];
    } catch {
      scenarioIds = [];
    }
  }
  return { ...row, scenario_ids: scenarioIds };
}

export function listTrades(): Trade[] {
  const rows = db().getAllSync<Trade & { scenario_ids?: string | null }>(
    "SELECT * FROM trades ORDER BY opened_at DESC, id DESC"
  );
  return rows.map(normalizeTradeRow);
}

const OPTIONAL_KEYS = TRADE_OPTIONAL_COLUMNS.map((c) => c.name);

export function createTrade(
  t: Partial<Trade> &
    Pick<
      Trade,
      "symbol" | "market" | "direction" | "setup" | "entry_price" | "stop_price" | "size" | "risk_amount"
    >
): Trade {
  const openedAt = t.opened_at ?? nowIso();
  const cols = [
    "symbol",
    "market",
    "direction",
    "setup",
    "entry_price",
    "stop_price",
    "size",
    "risk_amount",
    "notes",
    "opened_at",
  ];
  const vals: (string | number | null)[] = [
    t.symbol,
    t.market,
    t.direction,
    t.setup,
    t.entry_price,
    t.stop_price,
    t.size,
    t.risk_amount,
    t.notes ?? t.note ?? "",
    openedAt,
  ];

  for (const key of OPTIONAL_KEYS) {
    const v = (t as Record<string, unknown>)[key];
    if (v === undefined || v === null) continue;
    cols.push(key);
    if (key === "scenario_ids") {
      vals.push(typeof v === "string" ? v : JSON.stringify(v));
    } else {
      vals.push(v as string | number);
    }
  }

  const placeholders = cols.map(() => "?").join(",");
  const result = db().runSync(
    `INSERT INTO trades(${cols.join(",")}) VALUES(${placeholders})`,
    ...vals
  );
  const row = db().getFirstSync<Trade & { scenario_ids?: string | null }>(
    "SELECT * FROM trades WHERE id = ?",
    result.lastInsertRowId
  );
  if (!row) throw new Error("Trade non creato");
  return normalizeTradeRow(row);
}

export function closeTrade(
  tradeId: number,
  exitPrice: number,
  mistake: boolean,
  notes: string,
  opts?: { mae_r?: number | null; mfe_r?: number | null }
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

  const sets = [
    "status='closed'",
    "exit_price=?",
    "r_result=?",
    "mistake=?",
    "notes=?",
    "closed_at=?",
  ];
  const params: (string | number)[] = [
    exitPrice,
    Math.round(rResult * 1000) / 1000,
    mistake ? 1 : 0,
    mergedNotes,
    nowIso(),
  ];
  if (opts?.mae_r != null) {
    sets.push("mae_r=?");
    params.push(opts.mae_r);
  }
  if (opts?.mfe_r != null) {
    sets.push("mfe_r=?");
    params.push(opts.mfe_r);
  }
  params.push(tradeId);

  db().runSync(`UPDATE trades SET ${sets.join(", ")} WHERE id=?`, ...params);

  const updated = db().getFirstSync<Trade & { scenario_ids?: string | null }>(
    "SELECT * FROM trades WHERE id = ?",
    tradeId
  );
  return updated ? normalizeTradeRow(updated) : null;
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
