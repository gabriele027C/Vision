"""Playbook condizionale (FASE 5-BIS): schede educative, non predittive.

I testi provengono SOLO da data/playbook.json. I trigger usano gli stati
qualitativi di FASE 4 (PLAYBOOK_THRESHOLDS) — un solo punto di verità.
Il playbook legge lo stato, non altera watchlist/sizing/filtri.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config import FUNDING_EXTREME, PLAYBOOK_THRESHOLDS, RVOL_INTEREST

PLAYBOOK_PATH = Path(__file__).resolve().parent.parent / "data" / "playbook.json"

_REQUIRED_CARD = (
    "id", "famiglia", "titolo", "trigger", "lettura", "monitorare",
    "invalidazione", "errore_tipico", "lato_operativo", "footer",
)

_cache: dict | None = None


def load_playbook(path: Path | None = None, *, force: bool = False) -> dict:
    """Carica e valida il JSON. Errore esplicito se malformato."""
    global _cache
    if _cache is not None and not force and path is None:
        return _cache
    p = path or PLAYBOOK_PATH
    if not p.exists():
        raise FileNotFoundError(f"playbook non trovato: {p}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"playbook JSON malformato: {exc}") from exc
    if "scenari" not in data or not isinstance(data["scenari"], list):
        raise ValueError("playbook: manca lista 'scenari'")
    for i, card in enumerate(data["scenari"]):
        missing = [k for k in _REQUIRED_CARD if k not in card]
        if missing:
            raise ValueError(f"playbook scenari[{i}] manca campi: {missing}")
        if not isinstance(card["trigger"], dict):
            raise ValueError(f"playbook scenari[{i}].trigger non è un dict")
        if not isinstance(card["monitorare"], list):
            raise ValueError(f"playbook scenari[{i}].monitorare non è una lista")
    if "checklist_universali" not in data:
        raise ValueError("playbook: manca checklist_universali")
    if path is None:
        _cache = data
    return data


def classify_funding(funding: float | None, direction: str = "long") -> str | None:
    if funding is None:
        return None
    if direction == "long" and funding >= FUNDING_EXTREME:
        return "extreme_against_long"
    if funding <= -FUNDING_EXTREME:
        return "negative" if direction == "long" else "extreme_against_short"
    if funding < 0:
        return "negative"
    if funding > 0:
        return "positive"
    return "flat"


def classify_rvol(rvol: float | None) -> str | None:
    if rvol is None:
        return None
    thr = PLAYBOOK_THRESHOLDS.get("rvol", {})
    high = thr.get("high", RVOL_INTEREST)
    low = thr.get("low", 1.0)
    if rvol >= high:
        return "high"
    if rvol < low:
        return "low"
    return "normal"


def build_asset_state(row: dict, *, flow: dict | None = None) -> dict[str, Any]:
    """Stato qualitativo per matching trigger. Chiavi assenti = non disponibili."""
    flow = flow or {}
    state: dict[str, Any] = {}

    prezzo = flow.get("price_state") or row.get("price_state")
    if prezzo:
        state["prezzo"] = prezzo

    oi = flow.get("oi_state") if flow.get("oi_state") is not None else row.get("oi_state")
    if oi:
        state["oi"] = oi

    cvd = flow.get("cvd_state") if flow.get("cvd_state") is not None else row.get("cvd_state")
    if cvd:
        state["cvd"] = cvd

    fund = classify_funding(row.get("funding"), row.get("direction", "long"))
    if fund:
        state["funding"] = fund

    rv = classify_rvol(row.get("rvol"))
    if rv:
        state["rvol"] = rv

    # Eventi da setup / note esistenti
    setup = row.get("setup")
    if setup == "A":
        state["evento"] = "pullback"
    elif setup == "B":
        state["evento"] = "breakout"

    # Squeeze TF (FASE 3)
    if row.get("tf_4h", {}).get("squeeze") or row.get("entry_tf") in ("D", "4H"):
        # squeeze_d_or_4h se compressione 4H o setup B compression
        if row.get("tf_4h", {}).get("squeeze") or (
            setup == "B" and row.get("entry_tf") in ("D", "4H", None)
        ):
            state["squeeze_d_or_4h"] = True
    timing = row.get("timing") or []
    if any(t.get("timeframe") in ("1H", "15m") for t in timing):
        state["squeeze_1h_or_15m"] = True

    # Trend allineato
    if row.get("direction") == "long":
        state["trend"] = "up_aligned"
    elif row.get("direction") == "short" or row.get("bearish"):
        state["trend"] = "down_aligned"

    # Volume extreme: RVOL molto alto come proxy
    if row.get("rvol") is not None and float(row["rvol"]) >= 3.0:
        state["volume"] = "extreme"

    # Cascade proxy: OI collapse + volume extreme
    if state.get("oi") == "collapse" and state.get("volume") == "extreme":
        state["evento"] = "cascade"

    return state


def _trigger_match(trigger: dict, state: dict) -> bool:
    """AND tra chiavi; OR se valore è lista. Chiave assente nello stato → False."""
    for key, expected in trigger.items():
        if key not in state:
            return False
        actual = state[key]
        if isinstance(expected, list):
            if actual not in expected:
                return False
        else:
            # boolean True in trigger: stato deve essere truthy / uguale
            if isinstance(expected, bool):
                if bool(actual) != expected:
                    return False
            elif actual != expected:
                return False
    return True


def active_scenarios(asset_state: dict, playbook: dict | None = None) -> list[dict]:
    """Schede i cui trigger matchano. Protezioni (lato_operativo=false) prima."""
    pb = playbook or load_playbook()
    matched = [c for c in pb["scenari"] if _trigger_match(c["trigger"], asset_state)]
    matched.sort(key=lambda c: (c.get("lato_operativo", True), c["id"]))
    return matched


def scenario_ids_for_row(row: dict, flow: dict | None = None) -> list[str]:
    state = build_asset_state(row, flow=flow)
    return [c["id"] for c in active_scenarios(state)]


def primary_alert_scenario(row: dict, flow: dict | None = None) -> dict | None:
    """Primo scenario operativo (lato_operativo=true) per alert — mai protezioni."""
    state = build_asset_state(row, flow=flow)
    for c in active_scenarios(state):
        if c.get("lato_operativo"):
            return c
    return None


def universal_checklist(name: str = "pre_ingresso") -> list[str]:
    pb = load_playbook()
    return list(pb["checklist_universali"].get(name, []))


__all__ = [
    "PLAYBOOK_PATH",
    "load_playbook",
    "classify_funding",
    "classify_rvol",
    "build_asset_state",
    "active_scenarios",
    "scenario_ids_for_row",
    "primary_alert_scenario",
    "universal_checklist",
]
