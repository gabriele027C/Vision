"""Cache TTL OI hist: due fetch entro TTL → una sola HTTP (mock)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from data import binance_client


def test_open_interest_hist_cache_ttl_one_http(tmp_path, monkeypatch):
    cache_dir = tmp_path / "oi_hist"
    cache_dir.mkdir()
    monkeypatch.setattr(binance_client, "_OI_CACHE_DIR", cache_dir)

    payload = [
        {"timestamp": 1_700_000_000_000 + i * 14_400_000, "sumOpenInterest": "1000"}
        for i in range(10)
    ]
    calls = {"n": 0}

    def fake_get(url, params=None):
        calls["n"] += 1
        return payload

    monkeypatch.setattr(binance_client, "_get", fake_get)

    s1 = binance_client.open_interest_hist("BTCUSDT", period="4h", limit=30, use_cache=True)
    s2 = binance_client.open_interest_hist("BTCUSDT", period="4h", limit=30, use_cache=True)

    assert calls["n"] == 1, f"attesa 1 HTTP, ottenute {calls['n']}"
    assert len(s1) == 10 and len(s2) == 10
    assert float(s1.iloc[-1]) == 1000.0
    # File cache presente
    files = list(cache_dir.glob("*.json"))
    assert len(files) == 1
    assert json.loads(files[0].read_text(encoding="utf-8"))


def test_open_interest_hist_bypass_cache_hits_http_twice(tmp_path, monkeypatch):
    cache_dir = tmp_path / "oi_hist2"
    cache_dir.mkdir()
    monkeypatch.setattr(binance_client, "_OI_CACHE_DIR", cache_dir)
    payload = [{"timestamp": 1_700_000_000_000, "sumOpenInterest": "42"}]
    calls = {"n": 0}

    def fake_get(url, params=None):
        calls["n"] += 1
        return payload

    monkeypatch.setattr(binance_client, "_get", fake_get)
    binance_client.open_interest_hist("ETHUSDT", use_cache=False)
    binance_client.open_interest_hist("ETHUSDT", use_cache=False)
    assert calls["n"] == 2
