"""Test confluence: ordinamento, rinorm su n/d, mai esclusione."""
from engine.confluence import attach_confluence, confluence_score, sort_by_confluence


def test_full_components_crypto():
    row = {
        "market": "crypto",
        "setup": "A",
        "entry_tf": "D",
        "rs_score": 0.9,
        "cvd_state": "up",
        "oi_state": "up",
        "funding": 0.0001,
        "rvol": 2.0,
    }
    r = confluence_score(row)
    assert r["score"] > 80
    assert r["renorm"] is False
    assert all(v["status"] == "ok" for v in r["breakdown"].values())


def test_missing_oi_cvd_renorm_not_zero():
    """Stock senza OI/CVD: non penalizzata a zero — rinorm su disponibili."""
    stock = {
        "market": "stocks",
        "setup": "B",
        "entry_tf": "D",
        "rs_score": 0.85,
        "rvol": 1.8,
        # no oi/cvd/funding
    }
    r = confluence_score(stock)
    assert r["renorm"] is True
    assert r["breakdown"]["oi_expand"]["status"] == "n/d"
    assert r["breakdown"]["cvd_long"]["status"] == "n/d"
    assert r["breakdown"]["funding_ok"]["status"] == "n/d"
    assert r["breakdown"]["oi_expand"]["contrib"] is None
    # Con RS alto + tech + rvol, score deve restare elevato (non ~40 per zeri)
    assert r["score"] >= 70


def test_sort_does_not_drop_rows():
    rows = [
        {"market": "crypto", "setup": "A", "rs_score": 0.5, "symbol": "A",
         "cvd_state": "down", "oi_state": "flat", "funding": 0.0, "rvol": 1.0},
        {"market": "crypto", "setup": "A", "rs_score": 0.9, "symbol": "B",
         "cvd_state": "up", "oi_state": "up", "funding": 0.0, "rvol": 2.0},
    ]
    out = sort_by_confluence(rows)
    assert len(out) == 2
    assert out[0]["symbol"] == "B"
    assert out[0]["confluence"] >= out[1]["confluence"]


def test_attach_fields():
    row = {"market": "stocks", "setup": "A", "rs_score": 0.7, "rvol": 1.2}
    attach_confluence(row)
    assert "confluence" in row
    assert "confluence_breakdown" in row
