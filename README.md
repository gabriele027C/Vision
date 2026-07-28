# Vision

App semi-automatica per selezione dell'attenzione e controllo del rischio (strategia TVS).  
Documentazione operativa dettagliata: [`src/README.md`](src/README.md).  
Playbook: [`PLAYBOOK_VISION.md`](PLAYBOOK_VISION.md).  
Archivio ricerca (non modificare): [`research/`](research/).

## Deploy / restart backend (obbligatorio dopo pull)

Dopo `git pull` (o qualsiasi cambio a `src/backend/`), il processo uvicorn/Python **vecchio** continua a servire codice in memoria. Senza restart i prezzi live, lo scan e le API restano stale.

```bash
# 1. Ferma il processo sulla porta 8000 (Windows PowerShell)
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue |
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

# 2. Riavvia il backend dalla cartella corretta
cd src/backend
pip install -r requirements.txt   # solo se requirements sono cambiati
python -m uvicorn main:app --host 127.0.0.1 --port 8000

# 3. Frontend (se serve)
cd ../frontend
npm install   # solo se package.json è cambiato
npm run dev
```

Verifica rapida: `GET http://127.0.0.1:8000/api/state` deve riflettere `last_scan` recente e, sulle righe watchlist, `price_live: true` quando il refresh live è attivo.

**Non** lasciare due uvicorn sulla stessa porta: su Windows un bind fallito (`WinError 10013`) lascia spesso il processo vecchio in ascolto — uccidilo e riparti.

## Tag di riferimento

- `post-audit-baseline` — stato consolidato post-audit FASI 0–5 (vedi `AUDIT_FASI_0-5.md`).
