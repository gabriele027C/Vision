# Vision Knowledge Base — Todo List

> Ultimo aggiornamento: 12 Maggio 2026
> Stato: Pipeline funzionante con 32 fonti, 7857 chunk, Google gemini-embedding-2

---

## PRIORITÀ ALTA

### 1. Riavviare Cursor e testare MCP in chat reale
- [ ] Riavviare Cursor per caricare `.cursor/mcp.json`
- [ ] Verificare che il tool `search_vision_docs` appaia tra gli MCP disponibili
- [ ] Testare con query reali in una sessione di sviluppo Vision
- [ ] Verificare che le Cursor Rules in `.cursor/rules/` vengano rispettate

### 2. Valutare la bontà dei chunk (quality audit)
- [ ] Selezionare 20-30 concetti chiave (Spring, OBI, CVD, VWAP, RVOL, Delta, Market Profile, ecc.)
- [ ] Per ogni concetto: cercare nel RAG e verificare che il chunk restituito sia completo e coerente
- [ ] Controllare che nessun chunk tagli a metà una definizione, una formula o una tabella
- [ ] Verificare che i confini dei chunk rispettino le sezioni logiche dei libri
- [ ] Misurare distribuzione token/chunk (min, max, media, mediana) — ideale 500-1200
- [ ] Identificare chunk troppo corti (<200 token) o troppo lunghi (>1200) e capire perché
- [ ] Creare un report `docs/chunk_quality_report.md` con i risultati

### 3. Correggere i metadata delle categorie
- [ ] Molti libri sono taggati `"general"` invece di categorie specifiche
- [ ] Libri da correggere nel dizionario `BOOK_METADATA` in `02_chunk.py`:
  - `trading-systems-and-methods` → `strategy, systematic, technical_analysis`
  - `ssrn-1695596` → identificare il paper e assegnare categorie
  - `The Price Impact of Order Book Events` → `market_microstructure, order_book, formula`
  - `LimitOrderBook` (Avellaneda & Stoikov) → `market_microstructure, order_book, hft`
  - `Algorithmic and High-Frequency Trading` → `algorithmic_trading, hft, market_microstructure`
  - `Machine_Learning_For_Algorithmic_Trading` → `machine_learning, algorithmic_trading`
  - `Profit with the Market Profile` → `market_profile, volume`
  - `Options_Volatility_and_Pricing` → `volatility, options, formula`
  - `The handbook of portfolio mathematics` → `portfolio, risk, formula`
  - `lasse_heje_pedersen` → `quantitative, portfolio, risk`
  - `Active Portfolio Management` → `portfolio, risk, quantitative`
- [ ] Dopo la correzione: rilanciare `02_chunk.py` + `03_index.py`

---

## PRIORITÀ MEDIA

### 4. Aggiungere OCR per i 3 PDF scansione
- [ ] `elliott-wave-principle-key-to-market-behavior` (Elliott Wave) — 0 pagine estratte
- [ ] `Martin Pring on Market Momentum` — 0 pagine estratte
- [ ] `Options_Volatility_and_Pricing_Sheldon_N` — 0 pagine estratte
- [ ] Valutare tool: `marker-pdf`, `nougat`, o `surya` per OCR di qualità
- [ ] Estrarre, pulire, re-chunkare e re-indicizzare solo questi 3

### 5. Pulizia manuale dei Markdown estratti
- [ ] Rimuovere header/footer ripetuti (titolo libro, numero pagina su ogni blocco)
- [ ] Verificare che le formule matematiche chiave siano leggibili (le ~20 formule core di Vision)
- [ ] Ricostruire heading gerarchici (H1/H2/H3) dove mancano — migliora il chunking semantico
- [ ] Formattare tabelle importanti in Markdown
- [ ] Salvare le versioni pulite in `docs/knowledge/` (separato da `docs/raw/`)

### 6. Ricerca ibrida (vettoriale + keyword) per sigle e acronimi
- [ ] Aggiungere fallback keyword nel tool `search_vision_docs`:
  se la query contiene termini brevi uppercase (RVOL, OBI, CVD, VWAP, SOS, LPS),
  fare anche un filtro `$contains` sul testo dei chunk
- [ ] Testare con query tipo "RVOL", "OBI formula", "CVD calculation"
- [ ] Valutare se serve BM25 esterno o basta la logica interna

### 7. Deduplicazione risultati
- [ ] Quando due chunk consecutivi (stesso source, pagine adiacenti) appaiono nei risultati,
  restituire solo quello con score migliore o fonderli
- [ ] Implementare nel tool `search_vision_docs` del MCP server

### 8. Creare glossario sigle (`docs/glossary.md`)
- [ ] File con le 30-40 sigle chiave: RVOL, OBI, CVD, Delta, VWAP, SOS, LPS, PS, SC, AR, ST, ecc.
- [ ] Per ogni sigla: definizione breve, formula (se applicabile), modulo Vision di riferimento
- [ ] Referenziato nelle Cursor Rules così l'agente lo consulta per disambiguare

---

## PRIORITÀ BASSA

### 9. Mappare chunk di teoria ai moduli Vision
- [ ] Creare mapping concetto → modulo (es. "Spring detection" → `pattern_engine`)
- [ ] Aggiungere tag `modules` (lista) ai chunk di teoria — utile per filtraggio mirato
- [ ] Non forzare: usare solo dove il mapping è chiaro e naturale

### 10. Robustezza MCP server
- [ ] Aggiungere logging (file log per debug)
- [ ] Gestire errori di connessione Google API con retry e fallback
- [ ] Aggiungere timeout sulle query ChromaDB
- [ ] Testare comportamento con vector_store corrotto o mancante

### 11. `.gitignore` e sicurezza
- [ ] Creare `.gitignore`:
  - `vector_store/` (rigenerabile)
  - `.env` (contiene API key)
  - `docs/raw/` (rigenerabile dai PDF)
  - `docs/chunks/` (rigenerabile)
  - `__pycache__/`
- [ ] Verificare che la chiave Google API non sia committata

### 12. Performance e scalabilità
- [ ] Misurare tempo di risposta del MCP server su query tipiche
- [ ] Se lento: valutare cache delle query più frequenti
- [ ] Se il corpus cresce: valutare migrazione da ChromaDB a Qdrant o Weaviate

### 13. Script di re-indexing one-shot
- [ ] Creare `scripts/reindex_all.py` che esegue 01 → 02 → 03 in sequenza
- [ ] Utile dopo ogni modifica ai metadata, al chunking, o aggiunta di nuovi PDF

### 14. Aggiungere documentazione spec Vision
- [ ] Quando i documenti architetturali di Vision saranno pronti,
  aggiungerli in `docs/knowledge/` con `source_type: "spec"`
- [ ] Re-indicizzare con le nuove fonti

---

## NOTE

- La pipeline completa (estrazione → chunking → indexing) richiede ~10 minuti
- Per re-indicizzare dopo modifiche: `python scripts/02_chunk.py && python scripts/03_index.py`
- 3 PDF sono scansioni e attualmente non hanno testo (0 chunk): Elliott Wave, Martin Pring, Options Volatility
- Il filtro per `category` funziona solo se i metadata nel dizionario `BOOK_METADATA` coprono il filename
