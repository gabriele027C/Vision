"""Unit test Fase 4: funding estremo → veto (status 'blocked') — nessuna rete."""
from __future__ import annotations

from config import FUNDING_EXTREME
from services.scanner import apply_funding_to_row


def make_row(direction: str = "long") -> dict:
    return {
        "symbol": "TESTUSDT",
        "direction": direction,
        "status": "watch",
        "funding": None,
        "warnings": [],
    }


def test_extreme_funding_against_long_blocks():
    row = make_row("long")
    apply_funding_to_row(row, FUNDING_EXTREME * 2, funding_block=True)
    assert row["status"] == "blocked"
    assert row["funding"] == FUNDING_EXTREME * 2
    assert any("bloccato" in w for w in row["warnings"])


def test_extreme_funding_against_short_blocks():
    row = make_row("short")
    apply_funding_to_row(row, -FUNDING_EXTREME * 2, funding_block=True)
    assert row["status"] == "blocked"


def test_extreme_funding_in_favor_does_not_block():
    # Funding molto negativo FAVORISCE i long (gli short pagano i long)
    row = make_row("long")
    apply_funding_to_row(row, -FUNDING_EXTREME * 2, funding_block=True)
    assert row["status"] == "watch"
    assert row["warnings"] == []


def test_normal_funding_does_not_block():
    row = make_row("long")
    apply_funding_to_row(row, FUNDING_EXTREME / 2, funding_block=True)
    assert row["status"] == "watch"
    assert row["warnings"] == []
    assert row["funding"] == FUNDING_EXTREME / 2


def test_funding_block_disabled_falls_back_to_warning():
    row = make_row("long")
    apply_funding_to_row(row, FUNDING_EXTREME * 2, funding_block=False)
    assert row["status"] == "watch"  # non bloccato
    assert any("Funding estremo" in w for w in row["warnings"])


def test_none_funding_is_noop():
    row = make_row("long")
    apply_funding_to_row(row, None, funding_block=True)
    assert row["status"] == "watch"
    assert row["funding"] is None
    assert row["warnings"] == []


def test_config_default_blocks():
    # FUNDING_BLOCK = True in config → default bloccante
    row = make_row("long")
    apply_funding_to_row(row, FUNDING_EXTREME * 2)
    assert row["status"] == "blocked"


def test_triggered_row_gets_overridden_to_blocked():
    row = make_row("long")
    row["status"] = "triggered"
    apply_funding_to_row(row, FUNDING_EXTREME * 2, funding_block=True)
    assert row["status"] == "blocked"  # il veto vince sul trigger
