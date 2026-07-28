"""Confronto output parità: float con tolleranza relativa 1e-9, resto exact."""
from __future__ import annotations

import math
from typing import Any

REL_TOL = 1e-9
ABS_TOL = 1e-12


def _is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def values_equal(a: Any, b: Any, path: str = "") -> list[str]:
    """Ritorna lista di divergenze (stringhe path: detail)."""
    diffs: list[str] = []
    if a is None and b is None:
        return diffs
    if type(a) is not type(b) and not (_is_number(a) and _is_number(b)):
        # None vs missing handled by callers; allow int/float mix
        if a is None or b is None:
            diffs.append(f"{path}: {a!r} != {b!r}")
            return diffs
        if isinstance(a, (dict, list)) or isinstance(b, (dict, list)):
            diffs.append(f"{path}: type {type(a).__name__} != {type(b).__name__}")
            return diffs

    if _is_number(a) and _is_number(b):
        af, bf = float(a), float(b)
        if math.isnan(af) and math.isnan(bf):
            return diffs
        if not math.isclose(af, bf, rel_tol=REL_TOL, abs_tol=ABS_TOL):
            diffs.append(f"{path}: {af!r} != {bf!r} (rel_tol={REL_TOL})")
        return diffs

    if isinstance(a, dict) and isinstance(b, dict):
        keys = sorted(set(a) | set(b))
        for k in keys:
            pa = f"{path}.{k}" if path else k
            if k not in a:
                diffs.append(f"{pa}: missing in left")
            elif k not in b:
                diffs.append(f"{pa}: missing in right")
            else:
                diffs.extend(values_equal(a[k], b[k], pa))
        return diffs

    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            diffs.append(f"{path}: len {len(a)} != {len(b)}")
            return diffs
        for i, (x, y) in enumerate(zip(a, b)):
            diffs.extend(values_equal(x, y, f"{path}[{i}]"))
        return diffs

    if a != b:
        diffs.append(f"{path}: {a!r} != {b!r}")
    return diffs


def compare_outputs(py: dict, ts: dict) -> list[str]:
    return values_equal(py, ts, "")
