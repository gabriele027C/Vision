"""Unit test Fase 6: soglia squeeze, vol_ok shiftato, retry Binance, log funding."""
from __future__ import annotations

import logging

import httpx
import numpy as np
import pandas as pd
import pytest

from data import binance_client
from engine.indicators import bollinger_width
from engine.setups import setup_b_metrics, trigger_status_4h


# ---------- (a) Soglia squeeze sulle barre precedenti ----------


def test_squeeze_threshold_excludes_current_bar():
    # Volatilità in calo costante → BBW strettamente decrescente: la barra
    # corrente è il minimo assoluto e i due campioni (con/senza) differiscono.
    n = 250
    idx = pd.date_range("2020-01-01", periods=n, freq="D", tz="UTC")
    amp = np.linspace(5.0, 0.1, n)
    close = pd.Series(100 + amp * np.where(np.arange(n) % 2 == 0, 1.0, -1.0), index=idx)
    df = pd.DataFrame(
        {
            "open": close.shift(1).fillna(100.0),
            "high": close * 1.005,
            "low": close * 0.995,
            "close": close,
            "volume": np.full(n, 1e6),
        },
        index=idx,
    )
    m = setup_b_metrics(df, "long")  # default: SQUEEZE_LOOKBACK 60
    bbw = bollinger_width(df["close"])
    expected = float(bbw.iloc[-61:-1].quantile(0.10))  # 60 barre PRECEDENTI
    including_current = float(bbw.iloc[-60:].quantile(0.10))
    assert m["bbw_thresh"] == pytest.approx(expected)
    # Sanity: su questa serie i due campioni differiscono davvero
    assert expected != pytest.approx(including_current)


# ---------- (b) vol_ok con media shiftata ----------


def _df4h(volumes: list[float], closes: list[float]) -> pd.DataFrame:
    n = len(volumes)
    idx = pd.date_range("2024-01-01", periods=n, freq="4h", tz="UTC")
    c = pd.Series(closes, index=idx, dtype=float)
    return pd.DataFrame(
        {"open": c, "high": c * 1.001, "low": c * 0.999, "close": c,
         "volume": pd.Series(volumes, index=idx, dtype=float)},
        index=idx,
    )


def test_vol_ok_uses_previous_20_bars_mean():
    # Barra a volume 2000 in posizione -21: entra nella media shiftata (barre
    # -21..-2), non in quella che include la corrente. Volume corrente 150:
    # sopra la vecchia media (~102.5), sotto quella nuova (195) → NON triggered.
    volumes = [100.0] * 9 + [2000.0] + [100.0] * 19 + [150.0]  # 30 barre
    closes = [100.0] * 29 + [106.0]  # ultima chiusura sopra il trigger
    df = _df4h(volumes, closes)
    status = trigger_status_4h(df, "long", trigger=105.0)
    assert status == "near"  # senza conferma volume resta 'near', non 'triggered'


def test_vol_ok_triggers_with_genuine_volume():
    volumes = [100.0] * 29 + [500.0]
    closes = [100.0] * 29 + [106.0]
    df = _df4h(volumes, closes)
    assert trigger_status_4h(df, "long", trigger=105.0) == "triggered"


# ---------- (c) Retry con backoff su 429/5xx e timeout ----------


class FakeResponse:
    def __init__(self, status_code: int, payload=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {"ok": True}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=httpx.Request("GET", "http://x"),
                response=httpx.Response(self.status_code),
            )


def _patch_get(monkeypatch, outcomes: list):
    """outcomes: FakeResponse o eccezioni, uno per chiamata."""
    calls = {"n": 0}

    def fake_get(url, params=None):
        i = calls["n"]
        calls["n"] += 1
        out = outcomes[i]
        if isinstance(out, Exception):
            raise out
        return out

    monkeypatch.setattr(binance_client._client, "get", fake_get)
    monkeypatch.setattr(binance_client.time, "sleep", lambda s: None)
    return calls


def test_retry_on_429_then_success(monkeypatch):
    calls = _patch_get(
        monkeypatch,
        [FakeResponse(429), FakeResponse(500), FakeResponse(200, {"v": 1})],
    )
    assert binance_client._get("http://x") == {"v": 1}
    assert calls["n"] == 3


def test_retry_on_timeout_then_success(monkeypatch):
    calls = _patch_get(
        monkeypatch,
        [httpx.ReadTimeout("t"), FakeResponse(200, {"v": 2})],
    )
    assert binance_client._get("http://x") == {"v": 2}
    assert calls["n"] == 2


def test_persistent_5xx_raises_after_3_attempts(monkeypatch):
    calls = _patch_get(
        monkeypatch, [FakeResponse(503), FakeResponse(503), FakeResponse(503)]
    )
    with pytest.raises(httpx.HTTPStatusError):
        binance_client._get("http://x")
    assert calls["n"] == 3


def test_4xx_not_retried(monkeypatch):
    calls = _patch_get(monkeypatch, [FakeResponse(404)])
    with pytest.raises(httpx.HTTPStatusError):
        binance_client._get("http://x")
    assert calls["n"] == 1


# ---------- (d) funding_rate logga l'eccezione ----------


def test_funding_rate_logs_warning(monkeypatch, caplog):
    def boom(url, params=None):
        raise httpx.ConnectError("rete giù")

    monkeypatch.setattr(binance_client, "_get", boom)
    with caplog.at_level(logging.WARNING, logger="data.binance_client"):
        assert binance_client.funding_rate("BTCUSDT") is None
    assert any("funding rate" in r.message for r in caplog.records)
