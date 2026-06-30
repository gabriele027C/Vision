# Strategia Swing "Trend-Volume-Struttura" (TVS)

> **Profilo operativo:** Swing trading Daily/4H · Capitale < 5.000 € · Long & Short ·
> Drawdown massimo tollerato 20% · Esecuzione semi-automatica (screener/alert + entrata manuale)
>
> **Mercati:** Azioni USA liquide + Top crypto per capitalizzazione/volume

---

## 0. Filosofia e aspettative realistiche

Questa strategia non prevede il futuro. Sfrutta tre fenomeni documentati e persistenti nei mercati:

1. **I trend persistono** più di quanto il caso giustificherebbe (momentum) — Murphy, Pring.
2. **Il volume anticipa il prezzo**: l'ingresso di denaro istituzionale lascia tracce nei volumi prima che il movimento sia evidente — Wyckoff, Coulling.
3. **La struttura del prezzo** (massimi/minimi, rotture di livelli) definisce chi ha il controllo — Wyckoff, Grimes.

L'edge non sta nel singolo trade ma nella **ripetizione disciplinata**: tanti trade piccoli, perdite tagliate corte, profitti lasciati correre. Obiettivo realistico: **15–35% annuo** con drawdown sotto il 20%. Chi promette di più senza rischio proporzionale mente.

**Formula dell'aspettativa** (da verificare dopo 50 trade in demo):

```
Expectancy = (WinRate × AvgWin) − (LossRate × AvgLoss)
```

Con WinRate 40% e rapporto medio profitto/perdita di 2.2R, l'aspettativa è +0.28R per trade. Non serve avere ragione spesso: serve perdere poco quando si sbaglia.

---

## 1. Universo di asset

### Crypto (Binance/Bybit, coppie USDT)
- Top 20 per capitalizzazione **esclusi** stablecoin e token con volume 24h < 100M $.
- Short tramite perpetual futures (vedi §9 per regole sul funding).

### Azioni USA
- Solo titoli con: prezzo > 10 $, volume medio giornaliero > 1M di pezzi, ADR% > 2% (serve movimento per fare swing).
- Universo di partenza: componenti S&P 500 + Nasdaq 100 + eventuali momentum stock segnalate dallo screener.
- Short solo se il broker lo consente senza costi proibitivi; in alternativa, lato short solo su crypto.

---

## 2. Filtro di regime (il "semaforo")

**Mai operare contro il regime.** È il filtro che elimina la maggior parte delle perdite. Si valuta sul **Daily**, una volta al giorno.

### Azioni
| Condizione | Long consentiti | Short consentiti |
|---|---|---|
| SPY/QQQ sopra EMA200 daily **e** EMA50 inclinata su | ✅ | ❌ |
| SPY/QQQ sotto EMA200 daily **e** EMA50 inclinata giù | ❌ | ✅ |
| Condizioni miste (prezzo a cavallo delle medie) | ⚠️ size dimezzata | ⚠️ size dimezzata |
| VIX > 30 | ❌ nessuna nuova posizione | ❌ nessuna nuova posizione |

### Crypto
| Condizione | Long consentiti | Short consentiti |
|---|---|---|
| BTC sopra EMA200 daily e sopra EMA50 | ✅ (BTC + alt) | ❌ |
| BTC sotto EMA200 daily e sotto EMA50 | ❌ | ✅ |
| BTC tra le due medie | ⚠️ solo BTC/ETH, size dimezzata | ⚠️ solo BTC/ETH, size dimezzata |

> Razionale: la maggioranza delle alt segue BTC; comprare alt con BTC in downtrend è remare controcorrente (correlazione di regime).

---

## 3. Selezione: forza relativa + volume anomalo

Ogni sera lo screener ordina l'universo e popola la watchlist (max 10 asset). Criteri:

1. **Forza relativa (RS):** performance dell'asset a 20 e 60 giorni **vs** il benchmark (SPY per stock, BTC per crypto).
   - Per i long: solo asset nel **top 20%** di RS.
   - Per gli short: solo asset nel **bottom 20%** di RS.
2. **RVOL (volume relativo):** volume del giorno / media volume 20 giorni.
   - RVOL ≥ 1.5 segnala interesse istituzionale (concetto Wyckoff/Coulling: "effort").
3. **Trend tecnico:** prezzo sopra EMA50 daily per candidati long, sotto per candidati short.

> Principio: si comprano i più forti nei mercati forti e si shortano i più deboli nei mercati deboli. Mai "comprare perché è sceso tanto".

---

## 4. Setup A — Pullback in trend (il pane quotidiano)

**Logica:** in un trend sano, i ritracciamenti verso la zona di valore sono occasioni di ingresso a favore di trend con stop stretto.

**Condizioni (timeframe Daily):**
1. Trend definito: EMA20 > EMA50 > EMA200, tutte inclinate su (inverso per short).
2. Il prezzo ritraccia verso la zona EMA20–EMA50 **oppure** verso il 38–61.8% di Fibonacci dell'ultima gamba.
3. Il ritracciamento avviene con **volume in calo** (correzione tecnica, non distribuzione — Wyckoff/Coulling).
4. RSI(14) daily resta sopra 40 nel pullback (sotto 60 per short): il momentum di fondo è intatto — Pring.

**Trigger di entrata (timeframe 4H):**
- Rottura del massimo dell'ultima candela 4H di reazione (BOS minore a favore di trend), **con** volume della candela di rottura superiore alla media — conferma "effort + result".
- In alternativa: candela 4H di engulfing/rifiuto sulla zona di valore con chiusura nella metà superiore del range.

**Invalidazione:** se il pullback supera il 61.8% o chiude daily sotto EMA50 con volume alto, il setup è annullato.

---

## 5. Setup B — Breakout da compressione con volume

**Logica:** dopo una fase di contrazione della volatilità (accumulazione/re-accumulazione in termini Wyckoff), la rottura con volume tende a iniziare una nuova gamba direzionale.

**Condizioni (timeframe Daily):**
1. Compressione: Bollinger Band Width ai minimi degli ultimi 60 giorni (squeeze) **oppure** range laterale di almeno 3 settimane con escursione < 1.5× ATR.
2. Durante il range, chiusure progressivamente più vicine alla resistenza (assorbimento dell'offerta) e volumi in contrazione.
3. Contesto: il range si forma **sopra** EMA200 daily per breakout long (sotto per short).

**Trigger di entrata:**
- Chiusura daily oltre il livello del range con **RVOL ≥ 2**. Senza volume, niente trade: i breakout a basso volume falliscono con frequenza molto più alta (Coulling, Wyckoff "Sign of Strength").
- Ingresso alla chiusura daily o sul primo retest del livello rotto (preferibile per stop più stretto).

**Trappola da evitare:** se il prezzo rompe e rientra nel range entro 2 giorni (upthrust/spring fallito), uscire subito — è spesso il segnale opposto.

---

## 6. Stop loss — sempre definito PRIMA dell'ingresso

- **Setup A:** stop sotto il minimo dello swing di pullback − 0.5 × ATR(14) daily (sopra il massimo per short).
- **Setup B:** stop sotto il livello di rottura − 1 × ATR(14), oppure sotto il minimo del range se più vicino.
- Lo stop è un ordine reale sul mercato, **mai** mentale.
- Lo stop non si allarga MAI. Si stringe solo a favore (vedi §8).

Se la distanza dello stop supera 2.5 × ATR, il trade ha geometria sfavorevole: si salta.

---

## 7. Position sizing — il cuore della sopravvivenza

Modello **frazionale fisso** (Vince, *Handbook of Portfolio Mathematics*: la frazione di capitale rischiata domina il risultato di lungo periodo molto più del singolo segnale).

```
Rischio per trade = 1% del capitale          (es. 4.000 € → 40 €)
Size = Rischio per trade / (Entrata − Stop)
```

**Esempio:** capitale 4.000 €, entrata BTC a 100.000, stop a 96.000 (−4%).
Rischio = 40 € → Size = 40 / 4.000 × 100.000 = **1.000 € di posizione** (0.01 BTC).

**Limiti di portafoglio (non negoziabili):**
| Regola | Valore |
|---|---|
| Rischio per singolo trade | 1% (0.5% nelle prime 20 operazioni reali) |
| Posizioni aperte contemporanee | max 4 |
| Rischio aperto totale | max 4% |
| Rischio su asset correlati (es. 3 alt) | max 2% complessivo |
| Perdita settimanale → stop trading fino a lunedì | −3% |
| Perdita mensile → stop, revisione del journal | −6% |
| Drawdown dal massimo di equity → dimezza il rischio a 0.5% | −10% |
| Drawdown −15% | solo demo finché non si torna sopra −10% |

Con questi limiti il drawdown 20% è matematicamente molto improbabile: servirebbe una sequenza di ~25 perdite consecutive a rischio pieno.

---

## 8. Gestione della posizione e uscite

Definizione: **1R = distanza entrata→stop.**

1. **A +1R:** sposta lo stop a breakeven. Da qui il trade non può più costare denaro.
2. **A +2R:** chiudi **50%** della posizione (incassa). 
3. **Sul restante 50%:** trailing stop con uno dei due metodi (scegline uno e non cambiarlo):
   - chiusura daily sotto EMA20 (per short: sopra), oppure
   - trailing a 2.5 × ATR dal massimo raggiunto (chandelier).
4. **Time stop:** se dopo 10 giorni di borsa (o 10 giorni per crypto) il trade non ha raggiunto +1R, chiudi. Il capitale fermo è un costo.

**Vietato:** mediare al ribasso, rimuovere lo stop, raddoppiare dopo una perdita per "recuperare".

---

## 9. Regole specifiche per mercato

### Crypto
- **Funding rate (perpetual):** non aprire long se il funding è estremamente positivo (> 0.05% per 8h): affollamento long = rischio squeeze. Specularmente per short con funding molto negativo.
- **Weekend:** liquidità ridotta → niente nuove entrate da venerdì sera a domenica; le posizioni aperte tengono stop più ampi già definiti, non si toccano.
- **Eventi:** annunci Fed/CPI e grandi scadenze opzioni: nessuna nuova entrata nelle 12h precedenti.
- Leva massima sui perpetual: quella necessaria per la size calcolata in §7, mai per amplificare il rischio.

### Azioni
- **Earnings:** mai tenere una posizione piena attraverso la trimestrale. O si chiude prima, o si riduce al 25%.
- **Gap di apertura:** se un titolo apre oltre lo stop, esci alla prima opportunità — non sperare nel rientro.
- **Settori:** preferisci titoli nei 3 settori più forti (per i long) o più deboli (per gli short) a 20 giorni — la forza di settore è metà del movimento di un titolo.

---

## 10. Routine operativa (semi-automatica)

**La sera (20–30 minuti, dopo la chiusura USA):**
1. Aggiorna il regime (§2): semaforo long/short/neutro per stock e crypto.
2. Lo screener (TradingView screener o filtri equivalenti) produce i candidati per RS + RVOL (§3).
3. Per ogni candidato verifica a mano Setup A o B; se valido, calcola entrata/stop/size e imposta **alert sul trigger**.
4. Aggiorna stop e target delle posizioni aperte (§8).

**Quando suona l'alert:** apri il grafico, verifica che il trigger sia pulito (volume presente, niente news in corso), esegui con l'ordine già pianificato. Nessuna decisione improvvisata: l'alert esegue il piano, non lo crea.

**La domenica (30 minuti):** journal della settimana — per ogni trade: setup, R risultato, errore di esecuzione sì/no. Calcola win rate, R medio, expectancy progressiva.

---

## 11. Protocollo di validazione (obbligatorio prima del capitale reale)

Da De Prado e Chan: la maggior parte delle strategie muore per **overfitting e mancanza di test**, non perché l'idea era sbagliata.

1. **Fase demo: minimo 50 trade** su conto demo/paper trading, seguendo le regole alla lettera. Niente capitale reale prima.
2. Metriche da raccogliere:
   - Win rate, R medio dei vincenti, R medio dei perdenti
   - Expectancy per trade (deve essere > +0.15R per passare alla fase reale)
   - Max drawdown della curva demo
   - Profit factor (lordo profitti / lordo perdite; soglia: > 1.4)
3. **Fase reale ridotta:** primi 20 trade a 0.5% di rischio.
4. Solo dopo: rischio pieno all'1%.
5. **Revisione trimestrale:** se l'expectancy su 30+ trade scende sotto zero, si torna in demo e si analizza il journal — non si "aggiusta" la strategia a caso dopo 5 trade perdenti (campione insufficiente).

---

## 12. Checklist pre-trade (stampala)

```
□ Il regime (§2) consente questa direzione?
□ L'asset è nel top/bottom 20% di forza relativa?
□ Setup A o B completo su Daily? (non "quasi")
□ Trigger confermato su 4H con volume?
□ Stop definito e distanza ≤ 2.5 ATR?
□ Size calcolata = 1% di rischio (0.5% se in fase iniziale/drawdown)?
□ Rischio aperto totale dopo questo trade ≤ 4%?
□ Niente earnings/eventi macro nelle prossime 48h?
□ (Crypto) Funding non estremo? Non è weekend?
□ Ordine stop REALE inserito insieme all'entrata?
```

Una sola casella vuota = niente trade. Il mercato riapre domani.

**Script TradingView:** `docs/tradingview_checklist.pine` — indicatore Pine con checklist in linguaggio semplice, legenda colori in basso a sinistra e candele colorate (azzurro/arancione = setup in costruzione, lime = trigger). Le voci "TU" (rischio aperto, funding, stop reale) restano manuali.

---

## 13. Perché questa strategia ha un edge (e quando non ce l'ha)

**Funziona perché combina tre filtri indipendenti** — regime (direzione del mercato), forza relativa (selezione dell'asset), volume+struttura (timing) — e ogni trade ha perdita massima predefinita con profitto potenziale ≥ 2× il rischio. L'asimmetria fa il lavoro.

**Soffrirà** nei mercati laterali e choppy prolungati (falsi breakout, pullback che non ripartono): è il costo di ogni approccio trend-following. Il filtro di regime e il limite di perdita settimanale servono esattamente a contenere questi periodi. Non esiste strategia che vince in ogni condizione di mercato: esiste la strategia che perde poco quando l'ambiente le è ostile.

---

## Fonti principali (corpus Vision)

- Wyckoff / Villahermosa — struttura, accumulazione, Sign of Strength, spring/upthrust
- Anna Coulling — analisi volume-prezzo, conferma dei breakout
- Murphy, Pring — trend, medie mobili, momentum, divergenze
- Adam Grimes — pullback in trend, geometria del trade
- Ralph Vince — sizing frazionale fisso, matematica del rischio
- Ernest Chan, Lopez de Prado — validazione, overfitting, protocollo di test
- David Aronson — scetticismo metodologico: nessun edge va creduto senza dati
