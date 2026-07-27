"""Prezzi live + coerenza status/rottura per la watchlist."""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from data import binance_client, stocks_client

log = logging.getLogger(__name__)

PRICE_REFRESH_TTL_S = 20


def reconcile_status_with_price(row: dict) -> None:
    """Allinea status a last_price vs rottura (long: triggered ⇒ prezzo ≥ trigger).

    Lo status 'triggered' nasce dalla conferma 4H allo scan; se il prezzo live
    è tornato sotto la rottura, non può restare triggered (timestamp diversi).
    Non promuove a triggered: quello richiede conferma volume 4H allo scan.
    """
    if row.get("status") == "blocked":
        return
    px = row.get("last_price")
    trig = row.get("entry_trigger")
    if px is None or trig is None:
        return
    try:
        px = float(px)
        trig = float(trig)
    except (TypeError, ValueError):
        return
    direction = row.get("direction", "long")
    status = row.get("status", "watch")
    if direction == "long":
        if status == "triggered" and px < trig:
            row["status"] = "near" if px >= trig * 0.99 else "watch"
            warn = "Prezzo live sotto rottura: stato riallineato (triggered era su close 4H)"
            warnings = row.setdefault("warnings", [])
            if warn not in warnings:
                warnings.append(warn)
        elif status == "watch" and px >= trig * 0.99:
            row["status"] = "near"
    else:
        if status == "triggered" and px > trig:
            row["status"] = "near" if px <= trig * 1.01 else "watch"
            warn = "Prezzo live sopra rottura short: stato riallineato (triggered era su close 4H)"
            warnings = row.setdefault("warnings", [])
            if warn not in warnings:
                warnings.append(warn)
        elif status == "watch" and px <= trig * 1.01:
            row["status"] = "near"


def fetch_live_prices(crypto_syms: list[str], stock_syms: list[str]) -> dict[str, float]:
    """Mappa symbol → prezzo corrente (crypto Binance, stocks Yahoo 1m)."""
    prices: dict[str, float] = {}
    if crypto_syms:
        prices.update(binance_client.last_prices(crypto_syms))
    if stock_syms:
        prices.update(stocks_client.last_prices(stock_syms))
    return prices


def apply_live_prices(rows: list[dict], prices: dict[str, float], *, asof: str | None = None) -> int:
    """Aggiorna last_price sulle row e riallinea status. Ritorna quanti aggiornati."""
    asof = asof or datetime.now(timezone.utc).isoformat(timespec="seconds")
    n = 0
    for row in rows:
        sym = row.get("symbol")
        if sym not in prices:
            continue
        row["last_price"] = round(prices[sym], 6) if prices[sym] < 1 else round(prices[sym], 4)
        row["price_live"] = True
        row["price_asof"] = asof
        reconcile_status_with_price(row)
        n += 1
    return n


class PriceRefreshGate:
    """Evita di martellare Yahoo/Binance a ogni poll UI."""

    def __init__(self, ttl_s: float = PRICE_REFRESH_TTL_S):
        self.ttl_s = ttl_s
        self._last = 0.0

    def allow(self, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        if now - self._last < self.ttl_s:
            return False
        self._last = now
        return True
