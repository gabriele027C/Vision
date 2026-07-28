"""Formatter display — niente notazione scientifica."""
from engine.display_fmt import fmt_px


def test_fmt_px_no_scientific_large_oi():
    assert fmt_px(104500) == "104,500.00"
    assert "e+" not in fmt_px(1.045e5).lower()
    assert fmt_px(64841.8) == "64,841.80"


def test_fmt_px_small():
    assert fmt_px(0.001234)  # no crash
    assert fmt_px(None) == "n/d"
