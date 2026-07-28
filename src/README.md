# Vision TVS — App web per la strategia swing

## Licenza

Copyright © 2025-2026 Gabriele. Uso personale/non commerciale secondo [`../LICENSE`](../LICENSE); uso commerciale solo con licenza scritta. MIT Expo: [`../vision-mobile/LICENSE-MIT`](../vision-mobile/LICENSE-MIT).

---

Implementa il flusso semi-automatico della strategia **TVS** (`docs/STRATEGIA_SWING.md`):
l'app scansiona i mercati e prepara i trade; l'esecuzione avviene manualmente sul
paper trading di TradingView; il journal integrato traccia il protocollo di
validazione dei 50 trade.

## Architettura

```
src/
├── backend/            # FastAPI (Python 3.11)
│   ├── main.py         # API REST + loop di scansione automatica
│   ├── config.py       # Parametri strategia e universo
│   ├── database.py     # SQLite: impostazioni, trades, alert
│   ├── data/           # Binance (crypto) e Yahoo Finance (azioni) — gratuiti
│   ├── engine/         # Indicatori, regime, screener RS/RVOL, Setup A/B, sizing
│   └── services/       # Scanner, alert Telegram, metriche journal
└── frontend/           # React + Vite + TypeScript (dashboard scura)
```

- **Dati crypto:** API pubblica Binance (spot + funding perpetual). Nessuna chiave.
- **Dati azioni:** Yahoo Finance via `yfinance`; costituenti S&P 500 (dataset GitHub)
  e Nasdaq 100 (API pubblica Nasdaq), cache 7 giorni.
- **Alert:** in-app + Telegram opzionale (bot gratuito via @BotFather).

## Avvio

```bash
# Terminale 1 — backend (porta 8000)
cd src/backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000

# Terminale 2 — frontend (porta 5174)
cd src/frontend
npm install
npm run dev
```

Apri **http://127.0.0.1:5174** (non usare la porta 5173: altre app Vite/PWA sul PC
possono avere un service worker registrato lì e il browser mostra l'app sbagliata). All'avvio il backend lancia subito una scansione
completa (crypto ~15s, azioni ~1-2 min) e poi ripete ogni N minuti (configurabile
nelle Impostazioni).

## Deploy / restart dopo `git pull`

Il backend **non** ricarica da solo il codice Python. Dopo ogni pull che tocca `src/backend/`:

1. Termina il processo sulla porta 8000 (altrimenti resta il binario/vecchio codice in memoria).
2. Rilancia `python -m uvicorn main:app --host 127.0.0.1 --port 8000` da `src/backend`.
3. Controlla `/api/state`: `last_scan` fresco e, se previsto, `price_live: true` sulle righe.

Dettaglio e comandi Windows: vedi [`../README.md`](../README.md).

## Flusso operativo

1. **Dashboard** — semaforo di regime (SPY/QQQ/VIX e BTC) + setup caldi + alert.
2. **Watchlist** — top 10 per mercato: forza relativa, RVOL, Setup A/B, trigger e stop.
3. **Trade Planner** — checklist §12 obbligatoria + size calcolata (1% di rischio,
   dimezzato in regime misto). I valori si copiano nel paper trading di TradingView.
4. **Journal** — registra apertura/chiusura: win rate, expectancy, profit factor,
   max drawdown e curva di equity in R. Barra di avanzamento dei 50 trade di validazione.
5. **Impostazioni** — capitale, % rischio, intervallo scansione, Telegram.

**Checklist su TradingView:** copia `docs/tradingview_checklist.pine` nel Pine Editor e aggiungilo al grafico dell'asset (timeframe Daily consigliato). Complementa il Trade Planner con i check visivi sul chart.

## Telegram (opzionale)

1. Su Telegram: `@BotFather` → `/newbot` → copia il token.
2. Scrivi un messaggio al bot, poi apri `https://api.telegram.org/bot<TOKEN>/getUpdates`
   e copia `chat.id`.
3. Inserisci token e chat id in Impostazioni → "Test Telegram".

## Note

- L'app **non esegue ordini**: TradingView non espone API per il paper trading.
  Il design è volutamente semi-automatico (vedi §10 della strategia).
- `journal_flow_smoke.py` è uno smoke test del flusso journal (backend attivo richiesto; non è un test pytest).
- Database SQLite e cache in `src/backend/` (esclusi dal versionamento).
