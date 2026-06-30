# Vision — Report RAG (sistema, stack tecnico, audit qualità)

Documento unico per **presentare** il retrieval aumentato della knowledge base Vision: pipeline dati, componenti usati in produzione (indicizzazione + MCP), e **risultati quantificati** dell’audit automatico (retrieval live su Chroma, stessi embedding del runtime).

---

## 1. Come funziona il RAG Vision

### 1.1 Pipeline end-to-end

| Fase | Script / componente | Output | Ruolo nel RAG |
|------|---------------------|--------|---------------|
| Estrazione PDF | `scripts/01_extract_pdf.py` (PyMuPDF); PDF scansionati → `scripts/01_extract_pdf_ocr.py` | `docs/raw/*.md` | Testo strutturato con marker `<!-- PAGE n -->` per tracciabilità pagina |
| Chunking | `scripts/02_chunk.py` (tiktoken `cl100k_base`, merge con conteggio token su testo giunto; confini **sentence-aware**; overlap) | `docs/chunks/all_chunks.json` | Unità di retrieval: testo + metadati (`source`, `page`, categorie, `tokens`) |
| Indicizzazione | `scripts/03_index.py` (Chroma persistente, batch, retry; resume o `--fresh`) | `vector_store/` | Vettori document/query allineati allo stesso modello di embedding |
| Consumo | `mcp_server/server.py` — `search_vision_docs`, `get_module_spec`, `list_sources` | risposte tool MCP | Retrieval semantico lato agente / IDE |

### 1.2 Stack tecnico (cosa usiamo)

| Layer | Scelta | Note operative |
|-------|--------|------------------|
| Vector DB | ChromaDB (`PersistentClient`, collection `vision_docs`) | Store locale sotto `vector_store/` (non versionato in git) |
| Embedding documenti e query | Google **gemini-embedding-2** (`google-genai`) | Stessa funzione usata in `03_index.py` e nell’audit; richiede `GOOGLE_API_KEY` in `.env` |
| Tokenizer chunk | tiktoken `cl100k_base` | Allineato a ecosistemi LLM comuni; budget chunk **300–1200** token, overlap **80** |
| Metadati | `source`, `page` / `page_end`, categorie, `tokens`, `source_type` | Citazioni e filtri per dominio (Wyckoff, Market Profile, ML, ecc.) |

### 1.3 Dimensioni corpus (istantanea audit)

- **Chunk JSON:** 8,868
- **Fonti distinte (metadata `source`):** 36
- **Token totali indicizzabili (somma `tokens` sui chunk):** 4,443,477


> **Allineamento indice:** nel vector store risultano **8,694** voci; il file chunk ne conta **8,868**. Dopo modifiche al corpus eseguire `python scripts/03_index.py` (o `--fresh` se serve azzerare) prima di interpretare l’audit.

---

## 2. Metriche di bontà (quantificazione)

L’audit combina **test RAG live** (45 query: 30 core + 15 complesse) con **controlli statici** su tutti i chunk (distribuzione token, euristiche di taglio a inizio/fine frase). Le metriche **non** sostituiscono una valutazione umana su answer generation: misurano **recupero documentale** e qualità strutturale del corpus.

### 2.1 Punteggio composito (0–100)

**Vision RAG Score (composito):** **95.0 / 100** — formula pesata sull’istantanea corrente:

| Componente | Peso | Contributo (punti 0–100) | Valore usato |
|--------------|------|-------------------------|---------------|
| Retrieval core (query con hit) | 35% | 100.0 | 30/30 trovati |
| Completezza euristica top-1 (core) | 25% | 100.0 | 30 completi su 30 con hit |
| Match fonte attesa (core, substring filename) | 15% | 70.0 | 21/30 |
| Retrieval query complesse | 15% | 100.0 | 15/15 trovati |
| Bordo chunk (`100 − % ends_mid_sentence`) | 10% | 95.0 | ends_mid_sentence = 4.96% |


**Interpretazione:** il punteggio riassume retrieval e coerenza strutturale rispetto a baseline dichiarata in `docs/chunk_quality_baseline.json`. Il **match fonte attesa** è intenzionalmente conservativo (sottostringhe sul nome file); un mancato match può corrispondere comunque a contenuto pertinente da un altro manuale.

---

## 3. Corpus e trend (file chunk)

**File:** `docs/chunks/all_chunks.json` — **8,868 chunk**
**Data audit:** 2026-05-14
**Confronto trend:** `docs/chunk_quality_baseline.json` — chunk_quality_report.md v2 — 2026-05-13

---

## 4. Distribuzione token per chunk

| Metrica | Attuale | Baseline (v2) | Delta |
|---------|---------|---------------|-------|
| Totale chunk | 8,868 | 7,857 | +1011.0 |
| Mediana token | 476.0 | 436 | +40.0 |
| Media token | 501.1 | 473.5 | +27.6 |
| Min / Max | 1 / 1200 | 28 / 1195 | |
| P10 / P90 | 321 / 731 | 249 / 736 | |

**Nel range 200–1200 token:** 8,677 (97.8%) — baseline 99.7%
**Chunk troppo corti (<200):** 191 (2.2%)
**Chunk troppo lunghi (>1200):** 0

> **Nota dimensione corpus:** rispetto allo snapshot intermedio (9,166 chunk, Post-OCR Elliott/Pring/Natenberg + drop 3 chunk Pring; chunking invariato. Conteggi taglio non salvati in report separato.) il delta è principalmente **+-298 chunk** dalla 2ª ed. Jansen (PDF nativo) oltre evoluzioni precedenti.

---

## 5. Test RAG — 30 concetti core

Query in linguaggio naturale; colonne: completezza euristica, **Match atteso** = il `source` del top-1 contiene una delle sottostringhe attese (filename).

| # | Concetto | Trovato | Distanza | Completo | Src ok | Match atteso | Problemi |
|---|----------|---------|----------|----------|--------|--------------|----------|
| 1 | Spring (Wyckoff) | SI | 0.1551 | Completo | SI | SI | Nessuno |
| 2 | Upthrust (Wyckoff) | SI | 0.1818 | Completo | SI | SI | Nessuno |
| 3 | Sign of Strength (SOS) | SI | 0.1819 | Completo | SI | SI | Nessuno |
| 4 | Accumulation Schematic | SI | 0.2157 | Completo | SI | SI | ends_mid_sentence |
| 5 | Composite Operator | SI | 0.2771 | Completo | SI | SI | Nessuno |
| 6 | OBV (On Balance Volume) | SI | 0.2034 | Completo | SI | NO | Nessuno |
| 7 | VWAP | SI | 0.2511 | Completo | SI | NO | Nessuno |
| 8 | RVOL (Relative Volume) | SI | 0.2172 | Completo | SI | NO | Nessuno |
| 9 | Volume Profile | SI | 0.1955 | Completo | SI | SI | Nessuno |
| 10 | Delta (Order Flow) | SI | 0.1981 | Completo | SI | NO | Nessuno |
| 11 | Market Profile (TPO) | SI | 0.1832 | Completo | SI | SI | Nessuno |
| 12 | Value Area (POC/VAH/VAL) | SI | 0.1895 | Completo | SI | NO | Nessuno |
| 13 | Initial Balance | SI | 0.1794 | Completo | SI | SI | Nessuno |
| 14 | Elliott Wave | SI | 0.2235 | Completo | SI | SI | starts_mid_sentence |
| 15 | Fibonacci Retracement | SI | 0.2367 | Completo | SI | SI | Nessuno |
| 16 | RSI Divergence | SI | 0.2444 | Completo | SI | NO | Nessuno |
| 17 | Bollinger Bands | SI | 0.2493 | Completo | SI | SI | Nessuno |
| 18 | Sharpe Ratio | SI | 0.26 | Completo | SI | NO | Nessuno |
| 19 | Mean Reversion | SI | 0.2044 | Completo | SI | SI | Nessuno |
| 20 | Cointegration | SI | 0.22 | Completo | SI | SI | Nessuno |
| 21 | Kelly Criterion | SI | 0.2095 | Completo | SI | NO | Nessuno |
| 22 | Portfolio Sizing / Optimal f | SI | 0.1474 | Completo | SI | NO | Nessuno |
| 23 | Limit Order Book | SI | 0.2151 | Completo | SI | SI | Nessuno |
| 24 | Bid-Ask Spread | SI | 0.2147 | Completo | SI | SI | Nessuno |
| 25 | Price Impact | SI | 0.1871 | Completo | SI | SI | Nessuno |
| 26 | Liquidity Sweep | SI | 0.2569 | Completo | SI | SI | Nessuno |
| 27 | Implied Volatility | SI | 0.2222 | Completo | SI | SI | starts_mid_sentence |
| 28 | Volatility Smile/Skew | SI | 0.2533 | Completo | SI | SI | Nessuno |
| 29 | Flow Toxicity (VPIN) | SI | 0.1712 | Completo | SI | SI | Nessuno |
| 30 | Triple Barrier Method | SI | 0.2445 | Completo | SI | SI | Nessuno |

---

## 6. Query complesse e specifiche (stress test)

| # | Concetto | Trovato | Distanza | Completo | Src ok | Match atteso | Problemi |
|---|----------|---------|----------|----------|--------|--------------|----------|
| 31 | Zigzag Elliott rules | SI | 0.1749 | Completo | SI | SI | Nessuno |
| 32 | Black-Scholes assumptions Natenberg | SI | 0.2188 | Completo | SI | SI | Nessuno |
| 33 | Walk-forward ML validation | SI | 0.2167 | Completo | SI | NO | Nessuno |
| 34 | Purged k-fold de Prado | SI | 0.2087 | Completo | SI | SI | Nessuno |
| 35 | Jansen feature engineering | SI | 0.1733 | Completo | SI | SI | Nessuno |
| 36 | Jansen CNN RNN HFT | SI | 0.2065 | Completo | SI | SI | Nessuno |
| 37 | VPIN vs PIN toxicity | SI | 0.1849 | Completo | SI | SI | Nessuno |
| 38 | Avellaneda-Stoikov inventory | SI | 0.1361 | Completo | SI | SI | Nessuno |
| 39 | Wyckoff UTAD vs UT | SI | 0.1579 | Completo | SI | SI | Nessuno |
| 40 | Market Profile excess | SI | 0.2101 | Completo | SI | NO | ends_mid_sentence |
| 41 | Kelly vs optimal f | SI | 0.1373 | Completo | SI | NO | Nessuno |
| 42 | Cointegration Johansen | SI | 0.1743 | Completo | SI | SI | Nessuno |
| 43 | GAN synthetic bars | SI | 0.1779 | Completo | SI | SI | Nessuno |
| 44 | Options Greeks second order | SI | 0.2418 | Completo | SI | SI | Nessuno |
| 45 | Microprice imbalance | SI | 0.2166 | Completo | SI | SI | Nessuno |

---

## 7. Dettaglio query RAG (core)

### Spring (Wyckoff)

- **Query:** "What is a Spring in Wyckoff methodology and how to identify it?"
- **Distanza coseno:** 0.1551
- **Source:** Wyckoff-Methodology-in-Depth-Ruben-Villahermosa.pdf (pag. 127)
- **Categorie chunk:** pattern,strategy,methodology
- **Token:** 340
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> Spring/Shakeout The term Spring is an abbreviation of the word "Springboard". This concept was presented by Robert G. Evans, an outstanding student of Richard D. Wyckoff and is a refinement of the original concept developed by Wyckoff, which is known as Terminal Shakeout. Wyckoff referred to this term as a position that reaches the market during th...

### Upthrust (Wyckoff)

- **Query:** "Explain the Upthrust event in Wyckoff distribution"
- **Distanza coseno:** 0.1818
- **Source:** the-wyckoff-methodology-in-depth-how-to-trade-financial-markets-logically-trading-and-investing-course-advanced-technical-analysis-book-1-1.pdf (pag. 150)
- **Categorie chunk:** pattern,strategy,methodology
- **Token:** 340
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> UPTHRUST AFTER DISTRIBUTION An Upthrust After Distribution is the bullish shock that occurs as a Phase C test event within the distribution and redistribution ranges. This is an upward movement whose aim is to go test the ability of buyers to take prices higher to reach a key area, such as the break of previous highs. Theoretically it is an Upthrus...

### Sign of Strength (SOS)

- **Query:** "What is Sign of Strength SOS in Wyckoff accumulation?"
- **Distanza coseno:** 0.1819
- **Source:** Wyckoff-Methodology-in-Depth-Ruben-Villahermosa.pdf (pag. 144)
- **Categorie chunk:** pattern,strategy,methodology
- **Token:** 438
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> To appreciate that we can really be before an SOS we want to see that the bullish movement has ease of movement and that it reaches the midpoint of the range. In addition, any regression now should remain above the Spring minimum to show strength. Minor SOS In the event that the upward movement fails to break the structure, this movement would be l...

### Accumulation Schematic

- **Query:** "Describe the full Wyckoff accumulation schematic with phases A through E"
- **Distanza coseno:** 0.2157
- **Source:** Wyckoff-Methodology-in-Depth-Ruben-Villahermosa.pdf (pag. 37)
- **Categorie chunk:** pattern,strategy,methodology
- **Token:** 302
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI
- **Problemi:** ends_mid_sentence

> Phase D. Bullish trend within the range. SOS. Sign of Strength. Bullish movement generated after the Phase C Test event that manages to reach the top of the range. Also called JAC. Jump Across the Creek. Creek jump. LPS. Last Point of Support. These are the rising troughs we find in the upward movement towards resistance. BU. Back Up. This is the l...

### Composite Operator

- **Query:** "Who is the Composite Operator in Wyckoff theory and what is their role?"
- **Distanza coseno:** 0.2771
- **Source:** Wyckoff-Methodology-in-Depth-Ruben-Villahermosa.pdf (pag. 8)
- **Categorie chunk:** pattern,strategy,methodology
- **Token:** 342
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> Richard Wyckoff Richard Wyckoff Richard Wyckoff (1873-1934) became a Wall Street celebrity. He was a forerunner in the investment world as he started as a stockbroker at the age of 15 and by the age of 25 already owned his own brokerage firm. The method he developed of technical analysis and speculation arose from his observation and communication...

### OBV (On Balance Volume)

- **Query:** "How does On Balance Volume OBV work as an indicator?"
- **Distanza coseno:** 0.2034
- **Source:** Technical-Analysis-Explained-Pring.pdf (pag. 568)
- **Categorie chunk:** momentum,technical_analysis
- **Token:** 319
- **Completezza:** complete
- **Match fonte attesa (euristica):** NO

> Volume II: Volume Indicators  ● 555 On Balance Volume On Balance Volume (OBV) was discovered by Joe Granville and published  in his book Granville’s New Key to Stock Market Proﬁts (Literary Licensing,  2011). The indicator is plotted as a continuous, cumulative line. It begins  with an arbitrary number, which rises and falls depending on what the...

### VWAP

- **Query:** "What is VWAP volume weighted average price and how is it used in trading?"
- **Distanza coseno:** 0.2511
- **Source:** trading-systems-and-methods.pdf (pag. 1824)
- **Categorie chunk:** strategy,systematic,technical_analysis
- **Token:** 331
- **Completezza:** complete
- **Match fonte attesa (euristica):** NO

> VWAP As a note, order executions can be placed as a VWAP, a volume-weighted average price. For larger positions, this would return an average price representing how actively the market traded at different levels throughout the day. It is most convenient for hedge funds that do not want to force prices higher by placing an excessively large buy orde...

### RVOL (Relative Volume)

- **Query:** "What is relative volume RVOL and how to interpret it?"
- **Distanza coseno:** 0.2172
- **Source:** trading-systems-and-methods.pdf (pag. 1881)
- **Categorie chunk:** strategy,systematic,technical_analysis
- **Token:** 308
- **Completezza:** complete
- **Match fonte attesa (euristica):** NO

> Relative Changes in Volume Whether using actual or tick volume, decisions made using, for example, 15- minute volume patterns should compare each 15 minutes of the current day with the same 15 minutes of the prior day or with the average of that 15-minute interval over some range of days. While it may be sensible to use increasing intraday volume a...

### Volume Profile

- **Query:** "Explain Volume Profile and how to read volume at price distribution"
- **Distanza coseno:** 0.1955
- **Source:** Wyckoff_2_0_Structures,_Volume_Prof.pdf (pag. 186)
- **Categorie chunk:** pattern,strategy,methodology
- **Token:** 544
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> Part 5. Volume Profile The Volume Profile is a variant of the Market Profile®, a tool designed by J. Peter Steidlmayer in 1985 for the Chicago Board of Trade (CBOT®). Steidlmayer was a trader and executive member in this important futures and options market for over 40 years. This new method of representing the auction was initially intended only f...

### Delta (Order Flow)

- **Query:** "What is delta in order flow analysis? Difference between bid and ask volume"
- **Distanza coseno:** 0.1981
- **Source:** Wyckoff_2_0_Structures,_Volume_Prof.pdf (pag. 171)
- **Categorie chunk:** pattern,strategy,methodology
- **Token:** 491
- **Completezza:** complete
- **Match fonte attesa (euristica):** NO

> There are different Footprint chart types based on: The nature of the data: it can be configured with time, range, volume, rotation etc. To the representation protocol: Profile, Delta, Imbalance, Histogram, Ladder or BID/ASK. It is a highly configurable tool that generally includes multiple functionalities although it basically analyzes executed or...

### Market Profile (TPO)

- **Query:** "What is Market Profile TPO time price opportunity and how to read it?"
- **Distanza coseno:** 0.1832
- **Source:** Profit with the Market Profile_ Identifying Market Value in Real Time.pdf (pag. 22)
- **Categorie chunk:** market_profile,volume
- **Token:** 403
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> 3 Market Profile Charts Key Profile Chart Elements Time Price Opportunity (TPO) The most basic unit or building block of a Market Profile chart is the  time price opportunity, or “TPO”. A time price opportunity is cre- ated or printed on the chart as soon as the market touches a specific  price at a specific point in time. A time price opportunity...

### Value Area (POC/VAH/VAL)

- **Query:** "Define Value Area, Point of Control POC, VAH and VAL in Market Profile"
- **Distanza coseno:** 0.1895
- **Source:** Wyckoff_2_0_Structures,_Volume_Prof.pdf (pag. 188)
- **Categorie chunk:** pattern,strategy,methodology
- **Token:** 350
- **Completezza:** complete
- **Match fonte attesa (euristica):** NO

> 5.2 Volume Profile Composition The volume profiles are visually observed on the chart as a horizontal histogram where their values are distributed according to the negotiation that each price level has had. Depending on the amount of contracts traded at each price level the form of the distribution will vary. The more transactions, the longer the l...

### Initial Balance

- **Query:** "What is the Initial Balance in Market Profile and why is it important?"
- **Distanza coseno:** 0.1794
- **Source:** Profit with the Market Profile_ Identifying Market Value in Real Time.pdf (pag. 118)
- **Categorie chunk:** market_profile,volume
- **Token:** 410
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> 99 Market Profile Structures This initial period is represented by the first two thirty minute  periods A and B. Together, these two periods will create the initial  trading range for the day. A wide initial trading range suggests one  of two possible types of Profile structures for the day. One possibil- ity is that the trading day will continue t...

### Elliott Wave

- **Query:** "Explain Elliott Wave theory with impulse and corrective waves"
- **Distanza coseno:** 0.2235
- **Source:** Technical Analysis of the Financial Markets by John J. Murphy.pdf (pag. 295)
- **Categorie chunk:** technical_analysis
- **Token:** 375
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI
- **Problemi:** starts_mid_sentence

> in that order of importance. Pattern refers to the wave patterns or formations that comprise the most important element of the theory. Ratio analysis is useful in determining retracement points and price objectives by measuring the relationships between the different waves. Finally, time relationships also exist and can be used to confirm the wave...

### Fibonacci Retracement

- **Query:** "How do Fibonacci retracement levels 0.618 0.382 work in trading?"
- **Distanza coseno:** 0.2367
- **Source:** trading-systems-and-methods.pdf (pag. 592)
- **Categorie chunk:** strategy,systematic,technical_analysis
- **Token:** 377
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> Each retracement level is a trading opportunity. If a rally is expected to stop at a 50% retracement, a short sale could be triggered automatically at that price. But anticipating a top and selling into a rising market have a high degree of risk. Price movement is not so precise that you can anticipate a target with a great degree of confidence. Ta...

### RSI Divergence

- **Query:** "How to identify and trade RSI divergence signals?"
- **Distanza coseno:** 0.2444
- **Source:** trading-systems-and-methods.pdf (pag. 1403)
- **Categorie chunk:** strategy,systematic,technical_analysis
- **Token:** 359
- **Completezza:** complete
- **Match fonte attesa (euristica):** NO

> MACD Divergence The simplest rules are based on using the MACD as the indicator to create a bearish divergence. Once the second rising price peak is identified, along with the corresponding MACD peak, the divergence sell signal comes when the MACD line crosses the MACD signal line as it moves lower. This is seen in Figure 9.25 at the end of April....

### Bollinger Bands

- **Query:** "How do Bollinger Bands work and what signals do they generate?"
- **Distanza coseno:** 0.2493
- **Source:** trading-systems-and-methods.pdf (pag. 1107)
- **Categorie chunk:** strategy,systematic,technical_analysis
- **Token:** 487
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> Rules for Using Bands Regardless of the type of band that is constructed, rules for using bands to generate trading signals are limited. The first decision to be made is whether the trading strategy is one that is always in the market (a reversal strategy), changing from long to short and back again as the bands are penetrated. If so, the following...

### Sharpe Ratio

- **Query:** "What is the Sharpe ratio and how to calculate risk-adjusted returns?"
- **Distanza coseno:** 0.26
- **Source:** Machine Learning for Algorithmic Trading (2nd Edition).pdf (pag. 155)
- **Categorie chunk:** machine_learning,algorithmic_trading
- **Token:** 337
- **Completezza:** complete
- **Match fonte attesa (euristica):** NO

> Expected returns and volatilities are not observable, but can be estimated as follows from historical data: Unless the risk-free rate is volatile (as in emerging markets), the standard deviation of excess and raw returns will be similar. For independently and identically distributed (IID) returns, the distribution of the SR estimator for tests of s...

### Mean Reversion

- **Query:** "Explain mean reversion strategy and how to test for stationarity"
- **Distanza coseno:** 0.2044
- **Source:** Ernest Chan - Algorithmic Trading.pdf (pag. 59)
- **Categorie chunk:** algorithmic_trading,quantitative
- **Token:** 558
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> 41 THE BASICS OF MEAN REVERSION and trading strategies that I depict in this chapter are all tailored to time se- ries mean reversion. There is another kind of mean reversion, called “cross- sectional” mean reversion. Cross-sectional mean reversion means that the  cumulative returns of the instruments in a basket will revert to the cumula- tive ret...

### Cointegration

- **Query:** "What is cointegration and how is it used in pairs trading?"
- **Distanza coseno:** 0.22
- **Source:** Quantitative_Trading_Ernest_P_Chan.pdf (pag. 149)
- **Categorie chunk:** algorithmic_trading,quantitative
- **Token:** 375
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> Special Topics in Quantitative Trading 127 a pair of stocks such that if you long one and short the other, the market value of the pair is stationary. If this is the case, then the two individual time series are said to be cointegrated. They are so described because a linear combination of them is integrated of or- der zero. Typically, two stocks t...

### Kelly Criterion

- **Query:** "Explain Kelly criterion formula for optimal position sizing"
- **Distanza coseno:** 0.2095
- **Source:** trading-systems-and-methods.pdf (pag. 3392)
- **Categorie chunk:** strategy,systematic,technical_analysis
- **Token:** 345
- **Completezza:** complete
- **Match fonte attesa (euristica):** NO

> Finding Optimal f Ralph Vince, in his popular book Portfolio Management Formulas,²⁸ focuses on optimal f, risk of ruin, and other practical items. The significance of this approach is the need to maximize the amount invested yet avoid the risk of ruin. Optimal f is the ideal amount of an investment that should be put at risk at any one time. First,...

### Portfolio Sizing / Optimal f

- **Query:** "How to determine optimal position size using optimal f and Kelly formula?"
- **Distanza coseno:** 0.1474
- **Source:** trading-systems-and-methods.pdf (pag. 3392)
- **Categorie chunk:** strategy,systematic,technical_analysis
- **Token:** 345
- **Completezza:** complete
- **Match fonte attesa (euristica):** NO

> Finding Optimal f Ralph Vince, in his popular book Portfolio Management Formulas,²⁸ focuses on optimal f, risk of ruin, and other practical items. The significance of this approach is the need to maximize the amount invested yet avoid the risk of ruin. Optimal f is the ideal amount of an investment that should be put at risk at any one time. First,...

### Limit Order Book

- **Query:** "How does a limit order book work? Explain bid ask queue and price levels"
- **Distanza coseno:** 0.2151
- **Source:** Machine Learning for Algorithmic Trading (2nd Edition).pdf (pag. 64)
- **Categorie chunk:** machine_learning,algorithmic_trading
- **Token:** 579
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> How to work with Nasdaq order book data The primary source of market data is the order book, which updates in real time throughout the day to reflect all trading activity. Exchanges typically offer this data as a real-time service for a fee; however, they may provide some historical data for free. In the United States, stock markets provide quotes...

### Bid-Ask Spread

- **Query:** "What determines the bid-ask spread and its relationship to liquidity?"
- **Distanza coseno:** 0.2147
- **Source:** Algorithmic and High-Frequency Trading - PDF Room.pdf (pag. 37)
- **Categorie chunk:** algorithmic_trading,hft,market_microstructure
- **Token:** 622
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> 20  A Primer on the Microstrnctme of Financial Markets  each other in bilateral personal transactions, via broker-intermediated over-the­ counter (OTC) deals, via specialised broker-dealer networks, on open electronic  markets, etc. Our focus is on trading and trading algorithms that take place in  large electronic markets, whether they be open exc...

### Price Impact

- **Query:** "What is market price impact of large orders and how to model it?"
- **Distanza coseno:** 0.1871
- **Source:** The Price Impact of Order Book Events.pdf (pag. 1)
- **Categorie chunk:** market_microstructure,order_book,formula
- **Token:** 421
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> Electronic copy available at: http://ssrn.com/abstract=1712822 The price impact of order book events Rama Cont, Arseniy Kukanov and Sasha Stoikov First version: 01 March 2011, This version: April 30, 2012 Abstract We study the price impact of order book events - limit orders, market orders and can- celations - using the NYSE TAQ data for 50 U.S. st...

### Liquidity Sweep

- **Query:** "What is a liquidity sweep or stop hunt and how smart money uses it?"
- **Distanza coseno:** 0.2569
- **Source:** the-wyckoff-methodology-in-depth-how-to-trade-financial-markets-logically-trading-and-investing-course-advanced-technical-analysis-book-1-1.pdf (pag. 83)
- **Categorie chunk:** pattern,strategy,methodology
- **Token:** 315
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> The professionals who are building their position are obliged to carry out this type of manoeuvre. Due to the magnitude of their positions, it is the only way they have to be able to trade in the markets. They need liquidity with which to match their orders and the shake event is a great opportunity to get it. The stop jumping of sell positions, as...

### Implied Volatility

- **Query:** "What is implied volatility and how does it relate to options pricing?"
- **Distanza coseno:** 0.2222
- **Source:** Volatility Trading sinclair PDF.pdf (pag. 136)
- **Categorie chunk:** volatility,options
- **Token:** 352
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI
- **Problemi:** starts_mid_sentence

> model, where implied volatility estimates future volatility and thus informs the pricing strategy for options. 2.Question How do behavioral finance concepts affect trading decisions and market pricing? Answer:Behavioral finance concepts, such as overreaction and underreaction, significantly influence trader behavior and market pricing. For instance...

### Volatility Smile/Skew

- **Query:** "Explain the volatility smile and skew across option strikes"
- **Distanza coseno:** 0.2533
- **Source:** Volatility Trading sinclair PDF.pdf (pag. 8)
- **Categorie chunk:** volatility,options
- **Token:** 314
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> Implied Volatility Dynamics Overview In this chapter, the focus shifts from measuring realized volatility to understanding the dynamics of implied volatility, akin to predicting how odds might shift in sports betting. Traders are interested in the spread between implied and realized volatility rather than trading them directly. Volatility Surface T...

### Flow Toxicity (VPIN)

- **Query:** "What is flow toxicity VPIN and how does it predict flash crashes?"
- **Distanza coseno:** 0.1712
- **Source:** ssrn-1695596.pdf (pag. 2)
- **Categorie chunk:** market_microstructure,hft,flow_toxicity,volume
- **Token:** 688
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> Electronic copy available at: http://ssrn.com/abstract=1695596 Electronic copy available at: http://ssrn.com/abstract=1695596 2          Flow Toxicity and Liquidity in a High Frequency World    ABSTRACT    Order flow is toxic when it adversely selects market makers, who may be unaware they are  providing liquidity at a loss. We present a new proced...

### Triple Barrier Method

- **Query:** "Explain the triple barrier labeling method by de Prado"
- **Distanza coseno:** 0.2445
- **Source:** DePradoAdvancesFinancial_BonusPDF.pdf (pag. 28)
- **Categorie chunk:** formula,machine_learning,quantitative
- **Token:** 464
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> (a) (b) FIGURE 3.1 Two alternative configurations of the triple-barrier method 28  SNIPPET 3.3 GETTING THE TIME OF FIRST TOUCH def getEvents(close,tEvents,ptSl,trgt,minRet,numThreads,t1=False): #1) get target trgt=trgt.loc[tEvents] trgt=trgt[trgt>minRet] # minRet #2) get t1 (max holding period) if t1 is False:t1=pd.Series(pd.NaT,index=tEvents) #3)...


### Dettaglio query complesse

### Zigzag Elliott rules

- **Query:** "Elliott wave zigzag corrective pattern rules: subdivisions of waves A B C and relationship to impulse context"
- **Distanza coseno:** 0.1749
- **Source:** elliott-wave-principle-key-to-market-behavior-by-frost-and-prechter_compress.pdf (pag. 89)
- **Categorie chunk:** pattern,wave_theory
- **Token:** 408
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> Chapter 2: Guidelines of Wave Formation 89 CORRECTIVE WAVES Zigzag Rules ¢ A zigzag always subdivides into three waves. ¢ Wave A always subdivides into an impulse or leading diagonal. ¢ Wave C always subdivides into an impulse or diagonal. ¢ Wave B always subdivides into a zigzag, flat, triangle or combina- tion thereof. ¢ Wave B never moves beyond...

### Black-Scholes assumptions Natenberg

- **Query:** "Black-Scholes European option pricing model assumptions and continuous hedging Natenberg"
- **Distanza coseno:** 0.2188
- **Source:** Options_Volatility_and_Pricing_Sheldon_N.pdf (pag. 405)
- **Categorie chunk:** volatility,options,formula
- **Token:** 414
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> Models and the Real World lishing a delta neutral hedge against the undert rehedging process himself over the life of the op in Chapter 5. If a model assumes, as most do, t! model assumes that one can continuously main market gaps, the assumptions on which the mo the values generated by the model are render application which attempts to replicate o...

### Walk-forward ML validation

- **Query:** "Walk-forward analysis or cross-validation for financial time series to avoid overfitting in backtests"
- **Distanza coseno:** 0.2167
- **Source:** trading-systems-and-methods.pdf (pag. 112)
- **Categorie chunk:** strategy,systematic,technical_analysis
- **Token:** 370
- **Completezza:** complete
- **Match fonte attesa (euristica):** NO

> In-Sample and Out-of-Sample Data Proper test procedures call for separating data into in-sample and out-of-sample sets. This will be discussed in Chapter 21, System Testing. For now, consider the most important points. All testing is overfitting the data, yet there is no way to find out if an idea or system works without testing it. By setting asid...

### Purged k-fold de Prado

- **Query:** "Purged k-fold cross-validation and embargo for financial machine learning preventing leakage"
- **Distanza coseno:** 0.2087
- **Source:** DePradoAdvancesFinancial_BonusPDF.pdf (pag. 66)
- **Categorie chunk:** formula,machine_learning,quantitative
- **Token:** 366
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> SNIPPET 7.3 CROSS-VALIDATION CLASS WHEN OBSERVATIONS  OVERLAP class PurgedKFold(_BaseKFold): ’’’ Extend KFold class to work with labels that span intervals The train is purged of observations overlapping test-label intervals Test set is assumed contiguous (shuffle=False), w/o training samples in between ’’’ def __init__(self,n_splits=3,t1=None,pctE...

### Jansen feature engineering

- **Query:** "How to engineer features from alternative data text for trading signals using NLP pipelines"
- **Distanza coseno:** 0.1733
- **Source:** Machine Learning for Algorithmic Trading (2nd Edition).pdf (pag. 461)
- **Categorie chunk:** machine_learning,algorithmic_trading
- **Token:** 350
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> 14 Text Data for Trading – Sentiment Analysis This is the first of three chapters dedicated to extracting signals for algorithmic trading strategies from text data using natural language processing (NLP) and machine learning (ML). Text data is very rich in content but highly unstructured, so it requires more preprocessing to enable an ML algorithm...

### Jansen CNN RNN HFT

- **Query:** "Convolutional neural networks or recurrent models applied to limit order book or high frequency trading data"
- **Distanza coseno:** 0.2065
- **Source:** Machine Learning for Algorithmic Trading (2nd Edition).pdf (pag. 569)
- **Categorie chunk:** machine_learning,algorithmic_trading
- **Token:** 467
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> 18 CNNs for Financial Time Series and Satellite Images In this chapter, we introduce the first of several specialized deep learning architectures that we will cover in Part 4. Deep convolutional neural networks (CNNs) have enabled superhuman performance in various computer vision tasks such as classifying images and video and detecting and recogniz...

### VPIN vs PIN toxicity

- **Query:** "Difference between VPIN order flow toxicity and probability of informed trading PIN Easley"
- **Distanza coseno:** 0.1849
- **Source:** DePradoAdvancesFinancial_BonusPDF.pdf (pag. 186)
- **Categorie chunk:** formula,machine_learning,quantitative
- **Token:** 647
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> 19.5.2 Volume-Synchronized Probability of Informed Trading  Easley et al. [2008] proved that E [VB −VS] = (1 −𝛼) (𝜀−𝜀) + 𝛼(1 −𝛿) (𝜀−(𝜇+ 𝜀)) + 𝛼𝛿(𝜇+ 𝜀−𝜀) = 𝛼𝜇(1 −2𝛿) and in particular, for a sufficiently large 𝜇, E[|VB −VS|] ≈𝛼𝜇 Easley et al. [2011] proposed a high-frequency estimate of PIN, which they named volume-synchronized probability of inform...

### Avellaneda-Stoikov inventory

- **Query:** "Avellaneda Stoikov market making model optimal bid ask spread inventory risk"
- **Distanza coseno:** 0.1361
- **Source:** LimitOrderBook.pdf (pag. 1)
- **Categorie chunk:** market_microstructure,order_book,hft
- **Token:** 534
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> High-frequency trading in a limit order book Marco Avellaneda & Sasha Stoikov October 5, 2006 Abstract We study a stock dealer’s strategy for submitting bid and ask quotes in a limit order book. The agent faces an inventory risk due to the diﬀusive nature of the stock’s mid-price and a transactions risk due to a Poisson arrival of market buy and se...

### Wyckoff UTAD vs UT

- **Query:** "Wyckoff Upthrust After Distribution UTAD compared to ordinary upthrust in accumulation"
- **Distanza coseno:** 0.1579
- **Source:** the-wyckoff-methodology-in-depth-how-to-trade-financial-markets-logically-trading-and-investing-course-advanced-technical-analysis-book-1-1.pdf (pag. 150)
- **Categorie chunk:** pattern,strategy,methodology
- **Token:** 340
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> UPTHRUST AFTER DISTRIBUTION An Upthrust After Distribution is the bullish shock that occurs as a Phase C test event within the distribution and redistribution ranges. This is an upward movement whose aim is to go test the ability of buyers to take prices higher to reach a key area, such as the break of previous highs. Theoretically it is an Upthrus...

### Market Profile excess

- **Query:** "James Dalton Market Profile single prints and minus development excess what they indicate"
- **Distanza coseno:** 0.2101
- **Source:** Technical Analysis of the Financial Markets by John J. Murphy.pdf (pag. 423)
- **Categorie chunk:** technical_analysis
- **Token:** 301
- **Completezza:** complete
- **Match fonte attesa (euristica):** NO
- **Problemi:** ends_mid_sentence

> Appendix B: Market Profile* INTRODUCTION The purpose of this writing is to illustrate what Market Profile is and to define its underlying principles. Before the early 1980s, the only technical tools available were the bar chart and the point and figure chart. Since then Market Profile® 1 was introduced to expand the arsenal of technical tools. Mark...

### Kelly vs optimal f

- **Query:** "Ralph Vince optimal f versus Kelly criterion for position sizing drawdown tradeoffs"
- **Distanza coseno:** 0.1373
- **Source:** trading-systems-and-methods.pdf (pag. 3392)
- **Categorie chunk:** strategy,systematic,technical_analysis
- **Token:** 345
- **Completezza:** complete
- **Match fonte attesa (euristica):** NO

> Finding Optimal f Ralph Vince, in his popular book Portfolio Management Formulas,²⁸ focuses on optimal f, risk of ruin, and other practical items. The significance of this approach is the need to maximize the amount invested yet avoid the risk of ruin. Optimal f is the ideal amount of an investment that should be put at risk at any one time. First,...

### Cointegration Johansen

- **Query:** "Johansen test for multiple cointegrating vectors in pairs trading statistical arbitrage"
- **Distanza coseno:** 0.1743
- **Source:** Machine Learning for Algorithmic Trading (2nd Edition).pdf (pag. 308)
- **Categorie chunk:** machine_learning,algorithmic_trading
- **Token:** 498
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> There are two approaches to testing for cointegration: The Engle-Granger two-step method The Johansen test We'll discuss each in turn before we show how they help identify cointegrated securities that tend to revert to a common trend, a fact that we can leverage for a statistical arbitrage strategy. The Engle-Granger two-step method The Engle-Grang...

### GAN synthetic bars

- **Query:** "Generative adversarial networks for synthetic financial time series evaluation realism"
- **Distanza coseno:** 0.1779
- **Source:** Machine Learning for Algorithmic Trading (2nd Edition).pdf (pag. 663)
- **Categorie chunk:** machine_learning,algorithmic_trading
- **Token:** 481
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> 21 Generative Adversarial Networks for Synthetic Time-Series Data Following the coverage of autoencoders in the previous chapter, this chapter introduces a second unsupervised deep learning technique: generative adversarial networks (GANs). As with autoencoders, GANs complement the methods for dimensionality reduction and clustering introduced in C...

### Options Greeks second order

- **Query:** "Charm vanna volga second order Greeks exposure for delta hedging options book"
- **Distanza coseno:** 0.2418
- **Source:** Options_Volatility_and_Pricing_Sheldon_N.pdf (pag. 134)
- **Categorie chunk:** volatility,options,formula
- **Token:** 348
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> Option Values and Changing Market C positions using the implied deita, and an option decays is usually more use decays. Knowing the total delta, gamma, trader determine beforehand how th conditions. Since all these numbers a pe calculated by adding up the sensi trader who has purchased five options with a gamma of 4.0 each, hasa total (+5 x 2.5} Si...

### Microprice imbalance

- **Query:** "Volume imbalance microprice or weighted mid price in order book short term signal"
- **Distanza coseno:** 0.2166
- **Source:** The Price Impact of Order Book Events.pdf (pag. 5)
- **Categorie chunk:** market_microstructure,order_book,formula
- **Token:** 459
- **Completezza:** complete
- **Match fonte attesa (euristica):** SI

> ∆P b k = δ Lb k −Cb k −Ms k D  (1) ∆P s k = −δ Ls k −Cs k −Mb k D  , (2) where δ is the tick size1. These relations are remarkably simple - they involve no parameters, the impact of all order book events is additive and depends only on their net imbalance. Although all of the subsequent analysis can be carried out separately for bid and ask pri...


---

## 8. Problemi di taglio (statico su tutti i chunk)

| Tipo | N. chunk | % attuale | Baseline % (v2) | Delta (pp) |
|------|----------|-------------|-----------------|------------|
| ends_mid_sentence | 440 | 4.96% | 44.8% | -39.8 pp |
| starts_mid_sentence | 1,501 | 16.9% | 16.2% | +0.7 pp |
| unbalanced_parens(-3) | 62 | 0.7% | - | - |
| unbalanced_parens(-4) | 31 | 0.3% | - | - |
| unbalanced_parens(-5) | 17 | 0.2% | - | - |
| unbalanced_parens(+3) | 17 | 0.2% | - | - |
| unbalanced_parens(+4) | 16 | 0.2% | - | - |
| unbalanced_brackets(-3) | 15 | 0.2% | - | - |
| unbalanced_parens(-6) | 13 | 0.1% | - | - |
| unbalanced_brackets(-4) | 9 | 0.1% | - | - |
| unbalanced_parens(-7) | 7 | 0.1% | - | - |
| unbalanced_parens(-8) | 7 | 0.1% | - | - |
| unbalanced_parens(+5) | 6 | 0.1% | - | - |
| unbalanced_brackets(+3) | 5 | 0.1% | - | - |

> Il **denominatore** è cresciuto (più chunk); confrontare sia **%** sia **assoluti**. Un calo di **pp** su `ends_mid_sentence` indica miglioramento del confine frase; se solo il conteggio assoluto sale ma la % scende, il corpus è più "pulito" ai bordi.

---

## 9. Audit categorie (conteggi per tag)

| Categoria | N. chunk | % |
|-----------|----------|---|
| technical_analysis | 3,478 | 39.2% |
| strategy | 1,997 | 22.5% |
| machine_learning | 1,668 | 18.8% |
| algorithmic_trading | 1,637 | 18.5% |
| formula | 1,361 | 15.3% |
| systematic | 1,221 | 13.8% |
| momentum | 816 | 9.2% |
| volatility | 715 | 8.1% |
| options | 715 | 8.1% |
| market_microstructure | 650 | 7.3% |
| quantitative | 601 | 6.8% |
| pattern | 587 | 6.6% |
| portfolio | 579 | 6.5% |
| risk | 579 | 6.5% |
| reinforcement_learning | 533 | 6.0% |
| evidence_based | 499 | 5.6% |
| volume | 489 | 5.5% |
| hft | 467 | 5.3% |
| price_action | 462 | 5.2% |
| market_structure | 408 | 4.6% |
| methodology | 387 | 4.4% |
| market_profile | 360 | 4.1% |
| wave_theory | 200 | 2.3% |
| order_book | 196 | 2.2% |
| flow_toxicity | 75 | 0.8% |
| time_series | 64 | 0.7% |

> Nessun chunk con categoria `general`.

---

## 10. Riepilogo, punteggio composito e baseline

| Criterio | Attuale | Baseline (v2) | Commento |
|----------|---------|---------------|----------|
| RAG core: trovati | 30/30 | 30/30 | = |
| RAG core: completi (euristica) | 30/30 | 29 | vs baseline |
| RAG complesse: trovati | 15/15 | n/d | stress test |
| Vision RAG Score (composito, v. §2.1) | **95.0/100** | n/d | pesi: retrieval 35%, completezza 25%, match fonte 15%, complesse 15%, bordo chunk 10% |
| Match fonte attesa (solo core) | 21/30 | n/d | sottostringhe filename |
| Match fonte attesa (solo complesse) | 12/15 | n/d | sottostringhe filename |
| Taglio `ends_mid_sentence` (% su corpus) | 4.96% | 44.8% | -39.8 pp |
| Token in range 200–1200 | 97.8% | 99.7% | |

### Interpretazione

1. **Corpus più grande (8,868 vs 7,857 chunk baseline v2):** più candidati al retrieval; le query ML possono atterrare sulla **2ª ed. Jansen** (PDF testo).
2. **Mid-sentence:** `02_chunk.py` applica **sentence-aware** split e trim; restano percentuali residue su `ends_mid_sentence` / `starts_mid_sentence` (liste, formule, OCR). La **%** resta il KPI principale vs baseline v2.
3. **Match atteso:** euristica grezza su nome file; un NO può essere comunque una risposta utile (fonte diversa ma corretta).

---
*Report generato da `scripts/chunk_quality_audit_v2.py` → `docs/RAG_report.md`*