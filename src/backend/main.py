"""Vision TVS — backend FastAPI.

Avvio:  uvicorn main:app --port 8000   (dalla cartella src/backend)
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import database
from engine.sizing import position_size
from services.alerts import send_telegram
from services.metrics import compute_metrics
from services.scanner import scanner

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
log = logging.getLogger("vision")


async def _scan_loop() -> None:
    while True:
        try:
            await asyncio.to_thread(scanner.run_scan)
        except Exception as exc:
            log.error("scan loop: %s", exc)
        interval = max(int(database.get_settings()["scan_interval_min"]), 5)
        await asyncio.sleep(interval * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    task = asyncio.create_task(_scan_loop())
    yield
    task.cancel()


app = FastAPI(title="Vision TVS", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Stato / scanner ----------

@app.get("/api/state")
def get_state():
    # Sempre riallinea PREZZO al live (force): evita chiusura daily stale in UI.
    snap = scanner.snapshot(refresh_prices=True)
    alerts = database.list_alerts()
    snap["alerts"] = alerts
    snap["unread_alerts"] = sum(1 for a in alerts if not a["read"])
    return snap


@app.post("/api/scan")
async def trigger_scan():
    if scanner.snapshot()["scanning"]:
        return {"started": False, "reason": "scan già in corso"}
    asyncio.get_running_loop().run_in_executor(None, scanner.run_scan)
    return {"started": True}


@app.post("/api/alerts/read")
def read_alerts():
    database.mark_alerts_read()
    return {"ok": True}


# ---------- Diagnostica filtri ----------

@app.get("/api/diagnostics/{market}")
def get_diagnostics(market: str, symbols: str | None = None):
    if market not in ("crypto", "stocks"):
        raise HTTPException(400, "market deve essere crypto o stocks")
    sym_list = [s.strip() for s in symbols.split(",") if s.strip()] if symbols else None
    return scanner.get_diagnostics(market, sym_list)


@app.get("/api/diagnostics/{market}/{symbol}")
def get_symbol_diagnostic(market: str, symbol: str):
    if market not in ("crypto", "stocks"):
        raise HTTPException(400, "market deve essere crypto o stocks")
    result = scanner.get_symbol_diagnostic(market, symbol)
    if result is None:
        raise HTTPException(404, f"diagnostica non disponibile per {symbol} — esegui una scansione")
    return result


# ---------- Playbook (FASE 5-BIS) ----------

@app.get("/api/playbook")
def get_playbook():
    from engine.playbook import load_playbook
    return load_playbook()


@app.get("/api/playbook/checklist/{name}")
def get_playbook_checklist(name: str):
    from engine.playbook import universal_checklist
    items = universal_checklist(name)
    if not items:
        raise HTTPException(404, f"checklist '{name}' non trovata")
    return {"name": name, "items": items}


# ---------- Sizing ----------

class SizingRequest(BaseModel):
    entry: float = Field(gt=0)
    stop: float = Field(gt=0)
    half_size: bool = False
    direction: str | None = None
    market: str = "crypto"
    funding_est: float | None = None
    days_held_est: float = 0.0


@app.post("/api/sizing")
def calc_sizing(req: SizingRequest):
    s = database.get_settings()
    result = position_size(
        s["capital"], s["risk_pct"], req.entry, req.stop, req.half_size,
        direction=req.direction, market=req.market,
        funding_est=req.funding_est, days_held_est=req.days_held_est,
    )
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


# ---------- Journal ----------

class TradeCreate(BaseModel):
    symbol: str
    market: str
    direction: str
    setup: str = "A"
    entry_price: float = Field(gt=0)
    stop_price: float = Field(gt=0)
    size: float = Field(gt=0)
    risk_amount: float = Field(ge=0)
    notes: str = ""
    # Campi opzionali FASE 0 (journal esteso) — null-safe, non rompono i client vecchi
    timeframe: str | None = None
    pattern: str | None = None
    oi_at_entry: float | None = None
    cvd_slope_at_entry: float | None = None
    funding_at_entry: float | None = None
    rvol_at_entry: float | None = None
    mae_r: float | None = None
    mfe_r: float | None = None
    note: str | None = None
    scenario_ids: list[str] | None = None


class TradeClose(BaseModel):
    exit_price: float = Field(gt=0)
    mistake: bool = False
    notes: str = ""
    mae_r: float | None = None
    mfe_r: float | None = None


@app.get("/api/trades")
def get_trades():
    return database.list_trades()


@app.post("/api/trades")
def post_trade(t: TradeCreate):
    return database.create_trade(t.model_dump(exclude_none=True))


@app.put("/api/trades/{trade_id}/close")
def put_close_trade(trade_id: int, body: TradeClose):
    result = database.close_trade(
        trade_id, body.exit_price, body.mistake, body.notes,
        mae_r=body.mae_r, mfe_r=body.mfe_r,
    )
    if result is None:
        raise HTTPException(404, "trade non trovato o già chiuso")
    return result


@app.delete("/api/trades/{trade_id}")
def remove_trade(trade_id: int):
    if not database.delete_trade(trade_id):
        raise HTTPException(404, "trade non trovato")
    return {"ok": True}


@app.get("/api/metrics")
def get_metrics():
    return compute_metrics()


# ---------- Settings ----------

class SettingsUpdate(BaseModel):
    capital: float | None = Field(default=None, gt=0)
    risk_pct: float | None = Field(default=None, gt=0, le=2.0)
    telegram_token: str | None = None
    telegram_chat_id: str | None = None
    scan_interval_min: int | None = Field(default=None, ge=5, le=240)


@app.get("/api/settings")
def get_settings():
    return database.get_settings()


@app.put("/api/settings")
def put_settings(body: SettingsUpdate):
    values = {k: v for k, v in body.model_dump().items() if v is not None}
    return database.update_settings(values)


@app.post("/api/settings/telegram/test")
def test_telegram():
    s = database.get_settings()
    ok = send_telegram(
        s["telegram_token"], s["telegram_chat_id"],
        "<b>Vision TVS</b> — test riuscito. Gli alert arriveranno qui.",
    )
    if not ok:
        raise HTTPException(400, "Invio fallito: controlla token e chat_id")
    return {"ok": True}
