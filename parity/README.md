# Parità Python ↔ TypeScript

Fixture sintetiche deterministiche + runner Py/TS + confronto (tolleranza float relativa `1e-9`).

```bash
python parity/generate_fixtures.py
python parity/run_parity.py
# oppure via pytest:
cd src/backend && python -m pytest test_parity_cross.py -q
```

Python è il riferimento: ogni divergenza va corretta allineando TypeScript (salvo bug evidente lato Py).
