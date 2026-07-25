"""Unit test Fase 3: RVOL nello screener (score combinato + hard filter)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from config import RVOL_INTEREST
from engine.screener import classify_candidates, rank_score


def make_trending_df(n: int = 250, last_volume_mult: float = 1.0) -> pd.DataFrame:
    """Serie in uptrend con RVOL dell'ultima barra controllato via moltiplicatore."""
    rng = np.random.default_rng(7)
    idx = pd.date_range("2020-01-01", periods=n, freq="D", tz="UTC")
    close = 100 * np.cumprod(1 + np.full(n, 0.002) + rng.normal(0, 0.001, n))
    vol = np.full(n, 1_000_000.0)
    vol[-1] *= last_volume_mult
    return pd.DataFrame(
        {
            "open": np.roll(close, 1),
            "high": close * 1.005,
            "low": close * 0.995,
            "close": close,
            "volume": vol,
        },
        index=idx,
    )


# ---------- rank_score ----------


def test_rank_score_long_rewards_rs_and_rvol():
    base = rank_score(0.9, 1.0, "long")
    assert rank_score(0.95, 1.0, "long") > base       # più RS → più score
    assert rank_score(0.9, 2.0, "long") > base        # più RVOL → più score


def test_rank_score_rvol_capped_at_2x_threshold():
    # Oltre 2× la soglia il contributo RVOL non cresce più
    at_cap = rank_score(0.9, RVOL_INTEREST * 2, "long")
    beyond = rank_score(0.9, RVOL_INTEREST * 10, "long")
    assert at_cap == beyond
    # Componente massima: 0.7*rs + 0.3
    assert abs(at_cap - (0.7 * 0.9 + 0.3)) < 1e-9


def test_rank_score_short_uses_mirrored_rs():
    # Short: RS 0.1 (debole) è forte quanto RS 0.9 per un long
    assert abs(rank_score(0.1, 1.0, "short") - rank_score(0.9, 1.0, "long")) < 1e-9


# ---------- classify_candidates: ordinamento ----------


def test_high_rvol_overtakes_slightly_better_rs():
    data = {
        "AAA": make_trending_df(last_volume_mult=1.0),   # RVOL ~1
        "BBB": make_trending_df(last_volume_mult=2.5),   # RVOL ~2.5
    }
    scores = {"AAA": 0.90, "BBB": 0.85}
    out = classify_candidates(data, scores, True, True, rvol_hard_filter=False)
    assert [c["symbol"] for c in out] == ["BBB", "AAA"]  # RVOL ribalta l'ordine RS
    assert all("rank_score" in c for c in out)
    assert out[0]["rank_score"] > out[1]["rank_score"]


def test_default_does_not_drop_low_rvol():
    data = {"AAA": make_trending_df(last_volume_mult=0.5)}  # RVOL ~0.5 < soglia
    out = classify_candidates(data, {"AAA": 0.95}, True, True, rvol_hard_filter=False)
    assert len(out) == 1  # variante default: ordina, non taglia


# ---------- classify_candidates: hard filter ----------


def test_hard_filter_drops_low_rvol_candidates():
    data = {
        "AAA": make_trending_df(last_volume_mult=0.5),  # sotto soglia
        "BBB": make_trending_df(last_volume_mult=2.0),  # sopra soglia
    }
    scores = {"AAA": 0.95, "BBB": 0.9}
    out = classify_candidates(data, scores, True, True, rvol_hard_filter=True)
    assert [c["symbol"] for c in out] == ["BBB"]


def test_hard_filter_none_falls_back_to_config_default():
    # RVOL_HARD_FILTER=False in config → il candidato sotto soglia resta
    data = {"AAA": make_trending_df(last_volume_mult=0.5)}
    out = classify_candidates(data, {"AAA": 0.95}, True, True, rvol_hard_filter=None)
    assert len(out) == 1
