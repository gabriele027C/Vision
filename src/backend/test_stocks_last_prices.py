"""Test parsing last_prices con MultiIndex yfinance (anche 1 ticker)."""
import pandas as pd

from data import stocks_client


def test_from_download_single_ticker_multiindex():
    idx = pd.date_range("2026-07-27 15:58", periods=2, freq="min", tz="America/New_York")
    cols = pd.MultiIndex.from_product([["DDOG"], ["Open", "High", "Low", "Close", "Volume"]], names=["Ticker", "Price"])
    data = pd.DataFrame(
        [
            [250.0, 251.0, 249.0, 250.5, 1000],
            [250.5, 252.0, 250.0, 251.87, 2000],
        ],
        index=idx,
        columns=cols,
    )

    # Accede alla helper interna via last_prices path: monkeypatch download
    calls = {"n": 0}

    def fake_download(tickers, **kwargs):
        calls["n"] += 1
        return data

    import data.stocks_client as sc

    orig = sc.yf.download
    sc.yf.download = fake_download
    try:
        out = stocks_client.last_prices(["DDOG"])
    finally:
        sc.yf.download = orig

    assert out == {"DDOG": 251.87}
    assert calls["n"] == 1  # 1m ok → no daily fallback
