"""Orchestratore parità: fixture → run_python + run_ts → compare.

Invocabile da pytest (`test_parity_cross.py`) o dalla CLI:
  python parity/run_parity.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARITY = Path(__file__).resolve().parent
FIXTURES = PARITY / "fixtures" / "synthetic.json"

sys.path.insert(0, str(PARITY))
sys.path.insert(0, str(ROOT / "src" / "backend"))

from compare import compare_outputs  # noqa: E402
from run_python import run as run_py  # noqa: E402


def ensure_fixtures() -> None:
    if not FIXTURES.exists():
        subprocess.check_call([sys.executable, str(PARITY / "generate_fixtures.py")], cwd=str(ROOT))


def find_node() -> str | None:
    return shutil.which("node")


def find_npx() -> str | None:
    return shutil.which("npx")


def run_typescript() -> dict:
    npx = find_npx()
    if not npx:
        raise RuntimeError("npx non disponibile")
    # Preferisci tsx locale se presente, altrimenti npx tsx
    cmd = [npx, "--yes", "tsx", str(PARITY / "run_ts.ts")]
    env = os.environ.copy()
    env["NODE_NO_WARNINGS"] = "1"
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"run_ts fallito (exit {proc.returncode}):\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    # tsx può stampare warning; prendi l'ultimo oggetto JSON
    text = proc.stdout.strip()
    if not text:
        raise RuntimeError(f"run_ts stdout vuoto. STDERR:\n{proc.stderr}")
    # Trova il primo '{'
    start = text.find("{")
    if start < 0:
        raise RuntimeError(f"run_ts non ha prodotto JSON:\n{text[:500]}")
    return json.loads(text[start:])


def run_parity() -> tuple[dict, dict, list[str]]:
    ensure_fixtures()
    py_out = run_py()
    ts_out = run_typescript()
    # Confronta solo le chiavi dominio (ignora engine label)
    left = {k: v for k, v in py_out.items() if k != "engine"}
    right = {k: v for k, v in ts_out.items() if k != "engine"}
    diffs = compare_outputs(left, right)
    return py_out, ts_out, diffs


def main() -> int:
    if find_node() is None:
        print("SKIP: Node.js non disponibile — impossibile eseguire runner TS")
        return 2
    try:
        py_out, ts_out, diffs = run_parity()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    out_dir = PARITY / "fixtures"
    (out_dir / "last_python.json").write_text(json.dumps(py_out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "last_typescript.json").write_text(json.dumps(ts_out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if diffs:
        print(f"FAIL: {len(diffs)} divergenze Py<->TS:")
        for d in diffs[:80]:
            print(f"  - {d}")
        if len(diffs) > 80:
            print(f"  ... +{len(diffs) - 80} altre")
        return 1
    print("PASS: parita Py<->TS entro tolleranza (rel 1e-9)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
