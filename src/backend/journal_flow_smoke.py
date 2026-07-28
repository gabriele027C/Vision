"""Smoke test del flusso journal: crea -> chiudi -> metriche -> elimina."""
import httpx

BASE = "http://127.0.0.1:8000"

t = httpx.post(BASE + "/api/trades", json={
    "symbol": "TESTUSDT", "market": "crypto", "direction": "long", "setup": "A",
    "entry_price": 100, "stop_price": 96, "size": 10, "risk_amount": 40,
}).json()
print("aperto:", t["id"], t["status"])

c = httpx.put(BASE + f"/api/trades/{t['id']}/close",
              json={"exit_price": 108, "mistake": False, "notes": "test"}).json()
print("chiuso con R:", c["r_result"])

m = httpx.get(BASE + "/api/metrics").json()
print("metriche:", {k: m[k] for k in ("closed_trades", "win_rate", "expectancy", "profit_factor")})

d = httpx.delete(BASE + f"/api/trades/{t['id']}").json()
print("eliminato:", d)
