"""Parità cross-runtime Python ↔ TypeScript (FASE audit BLOCCO 2).

Se Node/npx non è disponibile: skip esplicito (motivato).
Altrimenti fallisce su qualsiasi divergenza oltre 1e-9 relativo.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PARITY = ROOT / "parity"
sys.path.insert(0, str(PARITY))


def _node_available() -> bool:
    return shutil.which("node") is not None and shutil.which("npx") is not None


@pytest.mark.skipif(
    not _node_available(),
    reason="Node.js/npx non disponibile: runner TS della suite parity/ non eseguibile",
)
def test_python_typescript_parity():
    from run_parity import run_parity

    _py, _ts, diffs = run_parity()
    assert diffs == [], "Divergenze Py↔TS:\n" + "\n".join(diffs[:50])
