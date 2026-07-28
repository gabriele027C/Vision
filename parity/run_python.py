"""Runner Python: carica le stesse fixture e produce output JSON normalizzato."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "src" / "backend"
sys.path.insert(0, str(BACKEND))

import pandas as pd

from engine.confluence import confluence_score
from engine.flow import (
    build_flow_snapshot,
    classify_cvd,
    classify_oi,
    cvd_slope_normalized,
    oi_deltas_from_hist,
)
from engine.playbook import scenario_ids_for_row
from engine.sizing import position_size
from engine.setups import detect_setup_a, detect_setup_b
from engine.timeframes import compression_metrics, detect_compression

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "synthetic.json"


def _bars_to_df(bars: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(bars)
    return df.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]]


def _norm_sizing(raw: dict) -> dict:
    """Normalizza errori: confrontiamo campi strutturati + flag error_present."""
    out = dict(raw)
    if "error" in out:
        return {
            "error_present": True,
            "liq_safe": out.get("liq_safe", False),
            "liq_price": out.get("liq_price"),
            "leverage": out.get("leverage"),
        }
    out.pop("error", None)
    out["error_present"] = False
    return out


def _norm_metrics(m: dict | None) -> dict | None:
    if m is None:
        return None
    # Escludi bbw_* / e200 (TS interface non li espone nello stesso shape)
    keys = [
        "timeframe",
        "squeeze",
        "context_ok",
        "atr",
        "trigger",
        "stop",
        "stop_dist",
        "invalidation_atr_mult",
        "rvol",
        "last",
        "rng_high",
        "rng_low",
    ]
    return {k: m[k] for k in keys if k in m}


def _norm_detect(d: dict | None) -> dict | None:
    if d is None:
        return None
    return {
        "setup": d.get("setup"),
        "timeframe": d.get("timeframe"),
        "direction": d.get("direction"),
        "entry_trigger": d.get("entry_trigger"),
        "stop": d.get("stop"),
        "atr": d.get("atr"),
        "invalidation_atr_mult": d.get("invalidation_atr_mult"),
        "rvol": d.get("rvol"),
    }


def _norm_setup(d: dict | None) -> dict | None:
    if d is None:
        return None
    return {
        "setup": d.get("setup"),
        "direction": d.get("direction"),
        "entry_trigger": d.get("entry_trigger"),
        "stop": d.get("stop"),
        "atr": d.get("atr"),
    }


def run(fixtures: dict | None = None) -> dict:
    data = fixtures or json.loads(FIXTURES.read_text(encoding="utf-8"))

    oi_flags = [
        {"delta_24h": c["delta_24h"], "state": classify_oi(c["delta_24h"])}
        for c in data["oi_delta_cases"]
    ]
    cvd_flags = [
        {"slope": c["slope"], "state": classify_cvd(c["slope"])}
        for c in data["cvd_slope_cases"]
    ]

    oi_series = pd.Series(data["oi_hist"])
    deltas = oi_deltas_from_hist(oi_series, bars_per_day=data["oi_bars_per_day"])
    vol = data["taker"]["volume"]
    slope_up = cvd_slope_normalized(vol, data["taker"]["taker_buy_up"])
    slope_down = cvd_slope_normalized(vol, data["taker"]["taker_buy_down"])
    snap = build_flow_snapshot(
        oi_value=deltas["oi_value"],
        oi_delta_24h=deltas["oi_delta_24h"],
        oi_delta_3d=deltas["oi_delta_3d"],
        cvd_slope=slope_up,
        price_delta=0.02,
    )

    flow = {
        "oi_flags": oi_flags,
        "cvd_flags": cvd_flags,
        "oi_deltas": {
            "oi_value": deltas["oi_value"],
            "oi_delta_24h": deltas["oi_delta_24h"],
            "oi_delta_3d": deltas["oi_delta_3d"],
            "oi_state": classify_oi(deltas["oi_delta_24h"]),
        },
        "cvd_slopes": {
            "up": slope_up,
            "up_state": classify_cvd(slope_up),
            "down": slope_down,
            "down_state": classify_cvd(slope_down),
        },
        "snap": {
            "oi_state": snap["oi_state"],
            "cvd_state": snap["cvd_state"],
            "price_state": snap["price_state"],
            "combo_key": snap["combo_key"],
        },
    }

    compression: dict = {}
    for tf in data["compression_tfs"]:
        bars = data["ohlcv"][tf]
        df = _bars_to_df(bars)
        compression[tf] = {}
        for direction in data["compression_directions"]:
            compression[tf][direction] = {
                "metrics": _norm_metrics(compression_metrics(df, direction, tf)),
                "detect": _norm_detect(detect_compression(df, direction, tf)),
            }

    df_d = _bars_to_df(data["ohlcv"]["D"])
    levels = {
        "setup_a_long": _norm_setup(detect_setup_a(df_d, "long", "crypto")),
        "setup_a_short": _norm_setup(detect_setup_a(df_d, "short", "crypto")),
        "setup_b_long": _norm_setup(detect_setup_b(df_d, "long", "crypto")),
        "setup_b_short": _norm_setup(detect_setup_b(df_d, "short", "crypto")),
    }

    sizing = {}
    for case in data["sizing_cases"]:
        raw = position_size(
            case["capital"],
            case["risk_pct"],
            case["entry"],
            case["stop"],
            case["half_size"],
            case["direction"],
            case["max_leverage"],
            case["taker_fee"],
            case["market"],
            case["funding_est"],
            case["days_held_est"],
        )
        sizing[case["id"]] = _norm_sizing(raw)

    confluence = {}
    for row in data["confluence_rows"]:
        rid = row["id"]
        payload = {k: v for k, v in row.items() if k != "id"}
        confluence[rid] = confluence_score(payload)

    playbook = {}
    for row in data["playbook_rows"]:
        rid = row["id"]
        payload = {k: v for k, v in row.items() if k != "id"}
        playbook[rid] = {"scenario_ids": scenario_ids_for_row(payload)}

    return {
        "engine": "python",
        "flow": flow,
        "compression": compression,
        "levels": levels,
        "sizing": sizing,
        "confluence": confluence,
        "playbook": playbook,
    }


def main() -> None:
    out = run()
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
