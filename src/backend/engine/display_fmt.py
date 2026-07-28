"""Formatter display condivisi (prezzi / quantità) — niente notazione scientifica."""
from __future__ import annotations


def fmt_px(x: float | None) -> str:
    """Prezzo/quantità leggibile: 104500 → '104,500.00', mai 1.045e+05."""
    if x is None:
        return "n/d"
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    ax = abs(v)
    if ax >= 1000:
        return f"{v:,.2f}"
    if ax >= 1:
        return f"{v:.2f}"
    if ax >= 0.01:
        return f"{v:.4f}"
    if ax >= 1e-8:
        s = f"{v:.10f}".rstrip("0").rstrip(".")
        return s or "0"
    return f"{v:.2e}"


def short_ts(iso_or_any: object | None) -> str:
    """Timestamp corto per etichette UI (YYYY-MM-DD HH:MM UTC se possibile)."""
    if iso_or_any is None:
        return "n/d"
    try:
        import pandas as pd

        ts = pd.Timestamp(iso_or_any)
        if ts.tzinfo is None:
            return ts.strftime("%Y-%m-%d %H:%M")
        return ts.tz_convert("UTC").strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        s = str(iso_or_any)
        return s[:16] if len(s) > 16 else s


def bar_asof_iso(df) -> str | None:
    """ISO timestamp dell'ultima barra del DataFrame (close D / TF)."""
    if df is None or len(df) == 0:
        return None
    try:
        import pandas as pd

        ts = pd.Timestamp(df.index[-1])
        if ts.tzinfo is None:
            ts = ts.tz_localize("UTC")
        else:
            ts = ts.tz_convert("UTC")
        return ts.isoformat()
    except Exception:
        try:
            return str(df.index[-1])
        except Exception:
            return None
