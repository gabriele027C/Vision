"""Genera fixture sintetiche deterministiche per la suite di parità Py↔TS.

Uso (dalla root):
  python parity/generate_fixtures.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "fixtures" / "synthetic.json"


def _lcg(seed: int):
    """PRNG lineare deterministico (Park–Miller)."""
    x = seed % 2147483647
    if x <= 0:
        x += 2147483646

    def nxt() -> float:
        nonlocal x
        x = (x * 48271) % 2147483647
        return x / 2147483647.0

    return nxt


def make_ohlcv(n: int, seed: int, start_px: float, start_ts: int, step_ms: int) -> list[dict]:
    """Serie OHLCV sintetica: trend + compressione finale (range stretto)."""
    rnd = _lcg(seed)
    bars: list[dict] = []
    px = start_px
    for i in range(n):
        # Fase 1: trend rialzista; fase 2: compressione (ultime ~40 barre)
        compress = i >= n - 40
        drift = 0.00015 if not compress else 0.00002
        noise = (rnd() - 0.5) * (0.008 if not compress else 0.0015)
        o = px
        c = px * (1.0 + drift + noise)
        if compress:
            # high/low stretti → squeeze BB più probabile
            wiggle = abs(c - o) * 0.5 + px * 0.0008
        else:
            wiggle = abs(c - o) + px * (0.004 + 0.003 * rnd())
        h = max(o, c) + wiggle
        l = min(o, c) - wiggle
        vol = 800.0 + 400.0 * rnd()
        if compress:
            vol *= 0.55
        bars.append(
            {
                "time": start_ts + i * step_ms,
                "open": round(o, 8),
                "high": round(h, 8),
                "low": round(l, 8),
                "close": round(c, 8),
                "volume": round(vol, 6),
            }
        )
        px = c
    return bars


def main() -> None:
    # MIN_BARS D=220 → genera 260 barre daily
    ohlcv = {
        "D": make_ohlcv(260, seed=42, start_px=100.0, start_ts=1_600_000_000_000, step_ms=86_400_000),
        "4H": make_ohlcv(160, seed=43, start_px=100.0, start_ts=1_600_000_000_000, step_ms=14_400_000),
        "1H": make_ohlcv(200, seed=44, start_px=100.0, start_ts=1_600_000_000_000, step_ms=3_600_000),
        "15m": make_ohlcv(240, seed=45, start_px=100.0, start_ts=1_600_000_000_000, step_ms=900_000),
    }

    # OI hist: 19 barre flat + spike (come test_flow_parity)
    oi_hist = [100.0] * 18 + [112.0]

    n = 20
    volume = [1000.0] * n
    taker_buy_up = [750.0] * n
    taker_buy_down = [200.0] * n

    oi_deltas_cases = [
        {"delta_24h": 0.06},
        {"delta_24h": 0.05},
        {"delta_24h": 0.049},
        {"delta_24h": -0.05},
        {"delta_24h": -0.19},
        {"delta_24h": -0.20},
        {"delta_24h": -0.25},
        {"delta_24h": None},
    ]
    cvd_slope_cases = [
        {"slope": 0.03},
        {"slope": 0.02},
        {"slope": 0.0},
        {"slope": -0.02},
        {"slope": -0.05},
        {"slope": -0.06},
        {"slope": None},
    ]

    sizing_cases = [
        {
            "id": "normal_1pct",
            "capital": 4000.0,
            "risk_pct": 1.0,
            "entry": 100.0,
            "stop": 99.0,
            "half_size": False,
            "direction": "long",
            "max_leverage": None,
            "taker_fee": 0.00055,
            "market": "crypto",
            "funding_est": None,
            "days_held_est": 3.0,
        },
        {
            "id": "leverage_cap",
            "capital": 1000.0,
            "risk_pct": 2.0,
            "entry": 100.0,
            "stop": 99.9,
            "half_size": False,
            "direction": "long",
            "max_leverage": 5.0,
            "taker_fee": 0.00055,
            "market": "crypto",
            "funding_est": 0.0003,
            "days_held_est": 2.0,
        },
        {
            "id": "liq_block_anomalous",
            "capital": 1000.0,
            "risk_pct": 5.0,
            "entry": 100.0,
            "stop": 75.0,
            "half_size": False,
            "direction": "long",
            "max_leverage": 20.0,
            "taker_fee": 0.00055,
            "market": "crypto",
            "funding_est": 0.0003,
            "days_held_est": 0.0,
        },
        {
            "id": "default_fee",
            "capital": 4000.0,
            "risk_pct": 1.0,
            "entry": 100.0,
            "stop": 95.0,
            "half_size": False,
            "direction": "long",
            "max_leverage": None,
            "taker_fee": None,
            "market": "crypto",
            "funding_est": None,
            "days_held_est": 0.0,
        },
        {
            "id": "stocks_2x",
            "capital": 10_000.0,
            "risk_pct": 1.0,
            "entry": 50.0,
            "stop": 48.0,
            "half_size": False,
            "direction": "long",
            "max_leverage": None,
            "taker_fee": 0.0,
            "market": "stocks",
            "funding_est": 0.0,
            "days_held_est": 0.0,
        },
    ]

    confluence_rows = [
        {
            "id": "crypto_full",
            "market": "crypto",
            "symbol": "PARITYUSDT",
            "direction": "long",
            "setup": "A",
            "entry_tf": "D",
            "rs_score": 0.85,
            "cvd_state": "up",
            "oi_state": "up",
            "funding": 0.0001,
            "rvol": 1.8,
        },
        {
            "id": "stock_no_flow",
            "market": "stocks",
            "symbol": "PARITY",
            "direction": "long",
            "setup": "B",
            "entry_tf": "D",
            "rs_score": 0.7,
            "cvd_state": None,
            "oi_state": None,
            "funding": None,
            "rvol": 1.2,
        },
        {
            "id": "crypto_weak_flow",
            "market": "crypto",
            "symbol": "WEAKUSDT",
            "direction": "long",
            "setup": "B",
            "entry_tf": "4H",
            "rs_score": 0.55,
            "cvd_state": "down",
            "oi_state": "flat",
            "funding": 0.0006,
            "rvol": 0.9,
        },
    ]

    playbook_rows = [
        {
            "id": "long_oi_cvd_confirm",
            "market": "crypto",
            "symbol": "BTCUSDT",
            "direction": "long",
            "setup": "A",
            "entry_tf": "D",
            "rs_score": 0.9,
            "rvol": 1.6,
            "funding": 0.00005,
            "last_price": 65000.0,
            "entry_trigger": 66000.0,
            "stop": 64000.0,
            "atr": 800.0,
            "status": "watch",
            "oi_state": "up",
            "cvd_state": "up",
            "price_state": "up",
            "oi_delta_24h": 0.08,
            "cvd_slope": 0.04,
        },
        {
            "id": "stock_minimal",
            "market": "stocks",
            "symbol": "AAPL",
            "direction": "long",
            "setup": "A",
            "entry_tf": "D",
            "rs_score": 0.8,
            "rvol": 1.1,
            "funding": None,
            "last_price": 190.0,
            "entry_trigger": 195.0,
            "stop": 185.0,
            "atr": 3.0,
            "status": "watch",
            "oi_state": None,
            "cvd_state": None,
            "price_state": "up",
        },
    ]

    payload = {
        "version": 1,
        "note": "Deterministic synthetic fixtures for Py↔TS parity. Do not edit by hand.",
        "ohlcv": ohlcv,
        "oi_hist": oi_hist,
        "oi_bars_per_day": 6,
        "taker": {
            "volume": volume,
            "taker_buy_up": taker_buy_up,
            "taker_buy_down": taker_buy_down,
        },
        "oi_delta_cases": oi_deltas_cases,
        "cvd_slope_cases": cvd_slope_cases,
        "sizing_cases": sizing_cases,
        "confluence_rows": confluence_rows,
        "playbook_rows": playbook_rows,
        "compression_directions": ["long", "short"],
        "compression_tfs": ["D", "4H", "1H", "15m"],
    }

    # sanity: no NaN
    def _check(obj, path=""):
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            raise ValueError(f"non-finite at {path}")
        if isinstance(obj, dict):
            for k, v in obj.items():
                _check(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _check(v, f"{path}[{i}]")

    _check(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
