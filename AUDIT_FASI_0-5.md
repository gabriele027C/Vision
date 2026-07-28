# AUDIT FASI 0–5 — Vision TVS

**Data audit:** 2026-07-28  
**Ruolo:** revisore esterno (nessuna correzione applicata durante la verifica)  
**HEAD commit:** `05543fd` (*Fix PREZZO watchlist…*) — branch `main` **ahead 11** vs `origin/main`  
**Working tree:** modifiche **non committate** su prezzi live / formattazione (`scanner.py`, `live_prices.py`, `diagnostics.py`, `WatchTable.tsx`, mirror mobile, ecc.)

---

## Tabella riassuntiva

| Area | Esito | Nota in una riga |
|------|-------|------------------|
| A1 Parità Py↔TS | **FAIL** | Esiste solo vettore OI/CVD Python; nessun runner che esegue TS e confronta sizing/compressione/confluence |
| A2 Linguaggio predittivo | **PARZIALE** | Niente BUY/SELL in UI app; restano «segnale» in playbook, «WR atteso», campo `trigger`, alert «entra in watchlist» |
| A3 Un solo punto di verità soglie | **PARZIALE** | OI/CVD in `PLAYBOOK_THRESHOLDS`; RVOL/funding ancora duplicati (`RVOL_INTEREST`, `FUNDING_EXTREME`, hardcode in `metrics.py`) |
| A4 Suite test | **PASS** | Backend `119 passed, 1 skipped` in 3.54s; skip Yahoo giustificato; `tsc --noEmit` EXIT 0 |
| A5 Archivio ricerca | **PARZIALE** | `diag_backtest.py` / `ablation_*` / report **untracked** (non in git); baseline 2-simboli **riprodotto** (n=23, WR 13.0%) |
| B FASE 0 Journal | **PARZIALE** | Migrazione idempotente OK; round-trip campi nuovi OK; breakdown TF/pattern vuoto sul DB reale (campi null sui closed) |
| C FASE 1 Sizing | **PARZIALE** | Cap leva e costi OK; blocco liquidazione esiste ma **irraggiungibile** a rischio 1% realistico; UI non disabilita esplicitamente su `liq_safe===false` se sizing presente |
| D FASE 2 Riposizionamento | **PARZIALE** | Short solo contesto (crypto watchlist long=0 in regime short); RSI tolto dal gate setup; PREZZO live dipende da codice **non pushato/non sempre nel processo** |
| E FASE 3 Multi-TF | **PASS** | Anti-lookahead, gate rate-limit, TF_PARAMS crescenti coperti da test |
| F FASE 4 OI/CVD | **PARZIALE** | Formula CVD verificata su kline reale; n/d su stock/PEPE OK; display OI in notazione scientifica (`1.045e+05`); TTL cache non verificato con mock HTTP in questo audit |
| G FASE 5 Confluence | **PASS** | Solo ordinamento; rinorm n/d; determinismo score su stessi input |
| H Prova d’uso | **FAIL** | Crypto long vuota; fix prezzi non consolidati su remote; diagnostica screener ≠ live; utente 8:00 non è autonomo |

---

## A — Audit trasversali

### A1 Parità Python ↔ TypeScript — **FAIL**

**Evidenza:**
- File presente: `src/backend/test_flow_parity.py` — calcola `parity_payload()` **solo in Python** e asserisce stabilità dei vettori; **non** invoca Node/TS.
- Nessun file tipo `test_*parity*sizing*`, `test_*compression*parity*`, `test_*confluence*parity*` trovato.
- `test_playbook_parity.py` esiste ma è limitato al playbook JSON, non al motore completo richiesto.

**Divergenze numeriche Py↔TS:** *non misurabili* — il test cross-runtime richiesto **manca**. Questo è un FAIL di copertura, non un PASS «silenzioso».

**Soglie OI/CVD TS** (controllo manuale): `vision-mobile/src/config.ts` espone `PLAYBOOK_THRESHOLDS.cvd.up/down = ±0.02` allineato a `config.py` — evidenza di allineamento **dichiarativo**, non di parità eseguibile.

### A2 Linguaggio predittivo residuo — **PARZIALE**

| Occorrenza | Dove | Contesto |
|------------|------|----------|
| «segnale» | `PLAYBOOK_VISION.md:203,310,379,381,396` | Playbook educativo / errori tipici |
| «WR atteso random» | `src/frontend/src/components/Journal.tsx:93` | Label UI journal |
| «segnale» / signal | `src/backend/engine/backtest.py` (doc/commenti ricerca) | Fuori UI live |
| Colonna / campo `entry_trigger`, header «Rottura» | `WatchTable.tsx:77,145` | Naming operativo ancora «trigger» a livello codice |
| Alert | `scanner.py:1152` | `"{sym} entra in watchlist: … rottura … invalidazione …"` — fattuale, ma verbo «entra» può suonare prescrittivo |

**Non trovati** in `vision-mobile/src` (grep): `BUY`, `SELL`, `probabilità`, `win rate atteso` come stringhe UI.

### A3 Un solo punto di verità soglie — **PARZIALE**

**Centralizzati:** `PLAYBOOK_THRESHOLDS`, `CONFLUENCE_WEIGHTS` in `config.py` / mirror TS.

**Duplicati / fuori PLAYBOOK_THRESHOLDS:**
- `RVOL_INTEREST = 1.5` e `RVOL_BREAKOUT = 2.0` in `config.py:27-28` usati da screener/setups; in parallelo `PLAYBOOK_THRESHOLDS["rvol"]["high"]=1.5` (`config.py:123-125`).
- `FUNDING_EXTREME = 0.0005` in `config.py:36`; riusato in scanner/confluence/playbook.
- `services/metrics.py:52-71` hardcode `0.0005`, `-0.05`, `-0.20`, `1.5` nei bucket contesto (non importano `PLAYBOOK_THRESHOLDS` / `FUNDING_EXTREME`).

### A4 Suite test — **PASS**

```
comando: cd src/backend && python -m pytest -q --tb=no
esito:   119 passed, 1 skipped in 3.54s
skip:    test_diagnostics.py:276 — "Yahoo non disponibile: ['Close']" (rete/Yahoo)
tsc:     vision-mobile npx tsc --noEmit → EXIT:0
```

Skip giustificato da dipendenza rete esterna → non conteggiato come FAIL prodotto.

### A5 Archivio ricerca + baseline backtest — **PARZIALE**

**Git:**
```
?? src/backend/diag_backtest.py
?? src/backend/ablation_study.py
?? src/backend/ablation_report.txt
?? src/backend/diag_report_*.txt
?? src/backend/vision1_report.txt
```
Non sono file tracciati: `git diff` su di essi è vuoto per definizione, ma **non sono protetti dal versionamento** (rischio perdita / non riproducibilità CI).

**Baseline 2 simboli** (eseguito in audit):
```
python -m engine.backtest --market crypto --symbols BTCUSDT,ETHUSDT --start 2022-01-01
→ backtest_trades.csv: n=23, WR=13.0%
```
Allineato al riferimento richiesto (23 trade, WR 13.0%).

---

## B — FASE 0 Journal — **PARZIALE**

| Check | Esito | Evidenza |
|-------|-------|----------|
| Migrazione 2× idempotente | **PASS** | Copia `vision_app.db`: `migrate1_added=[]`, `migrate2_added=[]`, `hash_stable_2nd=true` (`audit_probe_out.json`) |
| Record storici integri + null sui nuovi campi | **PASS** | Trade preesistenti: `timeframe`/`pattern`/`oi_at_entry`/… null (`sample_null_fields`) |
| Round-trip campi estesi | **PASS** | Trade id=24: `oi_at_entry=1e9`, `cvd_slope_at_entry=0.03`, `scenario_ids=["long_oi_cvd_confirm"]`, `timeframe=D`, `pattern=pullback` |
| Report expectancy TF/pattern/context + benchmark 33% | **PARZIALE** | `random_benchmark.expected_wr_pct=33.3` presente; `by_timeframe=[]`, `by_pattern=[]`, `by_context` vuoti sul DB reale perché i **closed** non hanno quei campi valorizzati. UI Journal mostra «WR atteso random» ma breakdown operativo vuoto in produzione. |

Nessuno screenshot UI journal allegato (verifica via API metrics / probe).

---

## C — FASE 1 Sizing bloccante — **PARZIALE**

### Output numerici

**(a) Spec: capital=4000, entry=100, stop=99, risk 1%**
```
leverage=1.0, leverage_capped=false, size_units=40, notional=4000,
cost_r=0.11, net_2r_after_costs=1.89, round_trip_cost=4.4
```
→ **non esercita** il cap di leva (leva implicita = 1×). Cap verificato solo con caso alternativo (capital=1000, stop=99.9, risk=2%): `leverage_capped=true`, `leverage=5.0`.

**(b) Liquidazione bloccante**
- Errore generabile: `position_size(1000, 150.0, 100, 75)` →  
  `"Stop (75) oltre il prezzo di liquidazione stimato (80) a leva 5.00x..."` (`liq_safe=false`).
- Con **rischio 1% realistico** e stop «oltre liquidazione», la leva implicita resta bassa → `liq_safe=true` (blocco **non raggiungibile** in uso normale).
- API: `main.py:133-134` alza `HTTPException(400)` se `"error" in result`.
- UI web (`Planner.tsx:314`): `disabled={!allChecked || !sizing || !symbol}` — **non** include `!sizingError` / `liq_safe`. Se l’API tornasse 200 con `error` nel body, il bottone non basterebbe; oggi l’API fa 400 e `sizing=null` → blocco indiretto. Mobile: stesso pattern (`PlannerScreen.tsx:247`).

**(c) Costi**
```
fee_round_trip=0.88, funding_cost_est=0.72 (days_held_est=3),
round_trip_cost=1.6, cost_r=0.04, net_2r_after_costs=1.96,
target_2r_net_long=110.2 > target_2r_long=110
```
Costi visibili in Planner (`Planner.tsx:285-286`).

**Pannello trade su asset reale:** non esercitato end-to-end in UI in questo audit (API sizing + codice UI verificati). Funding corrente mostrato se in watchlist crypto.

---

## D — FASE 2 Riposizionamento — **PARZIALE**

| Check | Esito | Evidenza |
|-------|-------|----------|
| Short non operativo | **PASS** (scan live 2026-07-28) | Regime crypto `mode=short`; `watchlist.crypto.length=0`; `bearish_context.crypto` popolato (5 simboli). |
| RSI non gate | **PASS** (codice) | `setups.py:295-307`: `detect_setup_a` non richiede più `momentum_ok`; RSI solo in metrics/diagnostica. |
| RS non esclude | **PASS** (codice + test screener) | `screener.py` / diagnostica: RS come warn/ranking. |
| Regime banner | **PASS** (codice) | `scanner.py:675` commento FASE 2; classify senza filtro regime operativo. |
| Alert fattuale | **PASS** (template) | Formato esatto in `scanner.py:1152-1154`: `"{symbol} entra in watchlist: {setup_label} + {rs_txt}, rottura {entry_trigger}, invalidazione {stop}, {fund_txt}"`. Nessun alert live catturato in Telegram in questa sessione (watchlist crypto vuota). |
| PREZZO/STATO coerenti | **PARZIALE** | Fix in working tree + `05543fd`; API stocks mostra `price_live=True` (es. IQV/HUM). **Non consolidato su origin** (`ahead 11` + diff locale). Diagnostica screener usa ancora close daily (`diagnostics.py:546-574`) ≠ live. Righe TRIGGERED crypto non osservabili (watchlist long vuota). |

---

## E — FASE 3 Multi-timeframe — **PASS**

| Check | Evidenza |
|-------|----------|
| Anti-lookahead / range esclude barra corrente | `test_timeframes.py:51-55`, `105-114` |
| Gate 1/asset/4h | `test_timeframes.py:82-87`; `TimingAlertGate` + `TIMING_ALERT_COOLDOWN_S` |
| Timing solo su watchlist | `scanner.py` timing loop su `rows` già in watchlist; `WATCHLIST_ENTRY_TFS=("D","4H")` |
| TF_PARAMS crescenti | `config.py:64-93`; `test_tf_params_documented_hypotheses` |

---

## F — FASE 4 OI/CVD — **PARZIALE**

| Check | Esito | Evidenza |
|-------|-------|----------|
| Formula CVD su kline reale | **PASS** | BTCUSDT 4h chiusa: `vol=46087.702`, `tbb=23134.938`; manuale `tbb-(vol-tbb)=182.174` = `bar_delta()` |
| Dati mancanti | **PASS** | `fetch_flow_snapshot('AAPL')` / `PEPEUSDT` → `combo_label='flusso non disponibile'`, stati `None`, senza crash |
| Cache TTL / retry 429 | **PARZIALE** | Codice: `OI_HIST_CACHE_TTL_S=3600`, retry in `binance_client._get`; **non** eseguito test con mock HTTP «due chiamate = una rete» in questo audit |
| except muti | **PASS** (flow path) | `flow_data.py:49` logga `log.warning`; client Binance logga warning |
| Snapshot at-entry journal | **PARZIALE** | Schema + round-trip probe OK; **Planner UI** non verificato a popolare automaticamente OI/CVD at-entry da watchlist in questo audit |
| Trascrizione display | **FAIL cosmetico/alto UX** | Diagnostica BTC live: messaggio `OI=1.045e+05 · Δ24h -0.44% (flat)` (`audit_btc_diag.json` / output API) — `{:.4g}` in `flow.py:259` |

---

## G — FASE 5 Confluence — **PASS**

| Check | Evidenza |
|-------|----------|
| Non filtra | Nessun `if confluence < …` in scanner; solo `sort_by_confluence` |
| Rinorm n/d | `test_confluence.py:22-39`; stock score ≥70 con OI/CVD `n/d` |
| Breakdown | Presente; API stocks es. `conf=98.4` |
| Determinismo | `confluence_score` stesso input → stesso score (`det True 95.6` in probe) |

Due scan live consecutivi «stessi cached» non rieseguiti (scan stocks/crypto completo ~minuti); determinismo unitario sì, E2E cached **non** dimostrato.

---

## H — Prova d’uso finale — **FAIL**

### Scan live osservato (API `127.0.0.1:8000`, 2026-07-28)

| Voce | Valore |
|------|--------|
| `last_scan` | `2026-07-28T17:04:56+00:00` |
| Crypto watchlist long | **0** |
| Stocks watchlist | **10** (prezzi `price_live=True`, confluence presente) |
| Diagnostica crypto | 11 simboli in cache; BTC con OI/CVD popolati |
| Tempo scan completo | Non cronometrato end-to-end in questa passata; storico sessione precedente ~crypto minuti + stocks 1–2 min download |

**Watchlist stocks (estratto API):** IQV/HUM/CVS con `price_live=True` e `confluence` 98.4 / 89.4 / 84.8.

**Diagnostica BTC (estratto):** `last_price≈63755.86`, flow OI flat / CVD down, messaggio OI in notazione scientifica.

**Pannello trade:** non esercitato su UI live (sizing verificato via API/unit).

### Domanda onesta (8:00 del mattino)

**No.** Un utente non ha tutto ciò che serve senza aprire il codice.

**Cosa manca esattamente:**
1. **Watchlist crypto long spesso vuota** in regime short senza guida UI su come usare il solo «contesto ribassista».
2. **Fix PREZZO / formattazione** non sono su `origin` (11 commit ahead + diff locale) → rischio di deploy/processo vecchio (già successo in sessione precedente).
3. **Diagnostica screener** mostra close daily, non prezzo live — senza etichetta esplicita confonde.
4. **OI in notazione scientifica** illeggibile.
5. **Journal breakdown** TF/pattern/context vuoto finché i trade closed non portano i campi nuovi.
6. **Blocco liquidazione sizing** non esercitabile a rischio 1% → falsa sicurezza.
7. **Nessuna garanzia di parità** app mobile vs backend Python su sizing/confluence/compressione.
8. Alert Telegram non osservabile senza situazioni long `triggered`.

---

## Difetti ordinati per gravità

### Bloccante
1. **Parità Py↔TS incompleta** — due client possono divergere silenziosamente (FAIL A1).
2. **Stato deploy incoerente** — `main` ahead 11 + fix prezzi solo locali; produzione può servire chiusure daily stale (evidenza storica sessione + git status).
3. **Sizing «blocco liquidazione» inefficace a parametri reali (1% rischio)** — requisito FASE 1(b) non soddisfatto in uso tipico.

### Alto
4. Diagnostica «Prezzo vs EMA50» senza distinzione close-daily vs live (confusione operativa).
5. Display OI `1.045e+05` (`flow.py:259` `{:.4g}`).
6. Soglie qualitative spezzate su più costanti (`RVOL_*`, `FUNDING_EXTREME`, hardcode `metrics.py`).
7. Archivio ricerca untracked — non protetto da git.
8. Journal report: expectancy per TF/pattern/context non utilizzabile sui dati storici esistenti (campi null).
9. Crypto long vuota senza UX di «cosa fare in regime short».

### Cosmetico / medio-basso
10. Residui linguistici («segnale» in playbook, «WR atteso random», naming `entry_trigger`).
11. Planner: disable button non esplicito su `sizingError` (solo indiretto via `sizing===null`).
12. Determinismo confluence E2E su due scan cached non dimostrato.
13. Test cache TTL OI / retry 429 non eseguito con mock in questo audit.

---

## Lista fix necessari (NON applicati — da approvare)

1. **Implementare suite parità eseguibile Py↔TS** (stessi input sintetici → assert su OI/CVD, compressione TF, livelli, sizing, confluence+breakdown); fallire CI su qualsiasi divergenza.
2. **Commit + push** (o release esplicita) di tutti i fix PREZZO/futures/fmt già in working tree; documentare restart obbligatorio del backend.
3. **Ridisegnare check liquidazione** così che a rischio ≤1–2% e leva ≤5× il caso «stop oltre liq» sia raggiungibile *oppure* documentare e testare solo lo scenario con rischio anomalo; allineare UI a `disabled={… \|\| !!sizingError \|\| sizing?.liq_safe===false}`.
4. In diagnostica: etichettare prezzi filtro come «close daily (filtro)» e opzionalmente mostrare «live» a parte.
5. Sostituire `{:.4g}` in `flow_filters_from_snapshot` con formatter trading (come `_fmt_px`).
6. Far dipendere i bucket `metrics.py` da `PLAYBOOK_THRESHOLDS` / `FUNDING_EXTREME`; eliminare duplicati RVOL dove possibile.
7. Tracciare in git (o archiviare fuori repo con README) `diag_backtest.py`, `ablation_study.py`, report.
8. Backfill o UX journal: spiegare che expectancy per TF/pattern appare solo dopo N trade con campi valorizzati; opzionale migrazione assistita.
9. UI regime short: messaggio dedicato su watchlist crypto vuota + link al contesto ribassista.
10. Grep cleanup copy predittiva residua in playbook/UI labels (senza alterare il senso educativo).
11. Aggiungere test integrazione: due `fetch_flow_snapshot` entro TTL → una sola HTTP (mock).
12. Verifica E2E: registrare trade da Planner con OI/CVD at-entry popolati da riga watchlist e assert DB.

---

## Artefatti evidenza (locali, generati in audit)

- `src/backend/audit_pytest_out.txt` — 119 passed / 1 skipped  
- `src/backend/audit_probe_out.json` — journal + sizing  
- `src/backend/audit_backtest_out.txt` + `backtest_trades.csv` — n=23, WR 13.0%  
- `src/backend/audit_btc_diag.json` — diagnostica BTC OI/CVD  
- `src/backend/audit_state_snap.json` — snapshot `/api/state`

---

*Fine report originale. Nessun fix applicato in quella sessione.*

---

## Post-fix (2026-07-28, BLOCCHI 1–6)

Tag baseline: `post-audit-baseline` @ `b35a445`.  
HEAD post-fix: `65339f2` su `origin/main` (git status pulito, allineato).

### Riesecuzione punti FAIL / PARZIALE

| Punto | Prima | Dopo | Evidenza |
|-------|-------|------|----------|
| **A1 Parità Py↔TS** | FAIL | **PASS** | `python parity/run_parity.py` → `PASS: parita Py<->TS entro tolleranza (rel 1e-9)`. Suite in `parity/` + `test_parity_cross.py`. **0 divergenze** al primo run (nessuna correzione TS necessaria). |
| **A5 Archivio ricerca** | PARZIALE | **PASS** | `research/` tracciato (`diag_backtest.py`, `ablation_study.py`, report, README). Baseline 2-simboli rieseguita: **n=23, WR r_net 13.0%**. |
| **C Sizing** | PARZIALE | **PASS** | Docstring rete di sicurezza (irraggiungibile a 1%/5x = corretto). Test anomalo `max_leverage=20` + risk alto vs normali. UI web/mobile: `disabled={… \|\| !!sizingError \|\| sizing?.liq_safe === false}`. |
| **D PREZZO / STATO** | PARZIALE | **PASS** | Fix prezzi pushati; diagnostica/watchlist etichettano `live` vs `close D` + timestamp; livelli come `livello`. Pannello regime short su watchlist crypto vuota. |
| **F display OI** | PARZIALE (display FAIL) | **PASS** | `fmt_px(104500) == "104,500.00"`; messaggio OI senza `e+`. Test `test_display_fmt.py`, `test_oi_cache.py`. |
| **H Prova d’uso** | FAIL | **PARZIALE** | Infrastruttura ok (deploy doc, parità, prezzi qualificati, sizing UI, journal note, OI at-entry). Resta: in regime short la watchlist long crypto è vuota *di proposito* (ora spiegata in UI); non ri-eseguito scan live end-to-end timed in questa passata. |

### Suite test post-fix

```
python -m pytest -q   → 127 passed, 1 skipped (Yahoo rete)
python parity/run_parity.py → PASS
npx tsc --noEmit (vision-mobile) → EXIT 0
```

### Domanda onesta aggiornata (8:00)

**Quasi sì, con un caveat.** Un utente che apre l’app dopo restart del backend ha: prezzi qualificati, sizing con blocco esplicito, journal con nota breakdown, pannello “regime short ≠ errore”, playbook e archivio ricerca.  
**Caveat:** se il regime crypto è short, non ci sono situazioni long operative — deve usare il tab contesto + playbook; non è un bug, ma richiede di leggere quel pannello.

### Fix list originale → stato

1–12 della lista precedente: **applicati** nei commit `ada60ac`…`65339f2` (BLOCCHI 1–6).

FASE 5-BIS: sbloccata solo dopo approvazione esplicita di questo Post-fix.
