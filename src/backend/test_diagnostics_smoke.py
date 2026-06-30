"""Smoke test pipeline diagnostica — esecuzione manuale o pre-release.

Uso (backend già in esecuzione su :8000):
    python test_diagnostics_smoke.py
"""
import sys
import time

import httpx

BASE = "http://127.0.0.1:8000"
VALID_STATUS = frozenset({"pass", "fail", "skip", "warn"})


def wait_scan(timeout_s: int = 180) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        r = httpx.get(f"{BASE}/api/state", timeout=10)
        r.raise_for_status()
        body = r.json()
        if not body.get("scanning"):
            return
        time.sleep(2)
    raise TimeoutError("scan non completata entro il timeout")


def assert_asset_structure(body: dict) -> None:
    assert "filters" in body["setup_a"]
    assert "filters" in body["setup_b"]
    for f in body["setup_a"]["filters"]:
        assert f["status"] in VALID_STATUS
    assert isinstance(body["blockers"], list)


def main() -> int:
    client = httpx.Client(timeout=30.0)
    try:
        client.get(f"{BASE}/api/state").raise_for_status()
    except Exception as exc:
        print(f"Backend non raggiungibile su {BASE}: {exc}")
        return 1

    print("Avvio scan...")
    client.post(f"{BASE}/api/scan").raise_for_status()
    wait_scan()
    print("Scan completata.")

    for market in ("stocks", "crypto"):
        r = client.get(f"{BASE}/api/diagnostics/{market}")
        r.raise_for_status()
        payload = r.json()
        assert "items" in payload and "symbols" in payload
        print(f"{market}: {len(payload['items'])} asset in cache diagnostica")
        if payload["items"]:
            sample = payload["items"][0]
            assert_asset_structure(sample)

        state = client.get(f"{BASE}/api/state").json()
        wl = state.get("watchlist", {}).get(market, [])
        if wl:
            sym = wl[0]["symbol"]
            one = client.get(f"{BASE}/api/diagnostics/{market}/{sym}").json()
            assert one["on_watchlist"] is True
            assert one["setup_a"]["eligible"] or one["setup_b"]["eligible"]
            assert_asset_structure(one)
            print(f"  watchlist {sym}: OK")

        if payload["items"]:
            off = next((i for i in payload["items"] if not i["on_watchlist"]), None)
            if off:
                assert len(off["blockers"]) >= 1 or not off["watchlist_eligible"]
                print(f"  off-watchlist {off['symbol']}: blockers={off['blockers'][:1]}")

    print("Smoke test diagnostica: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
