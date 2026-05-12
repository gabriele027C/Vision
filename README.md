# Vision — Knowledge Base & RAG Pipeline

Sistema di knowledge base per il progetto **Vision** (monitoraggio crypto e stock).
Trasforma manuali di trading, finanza quantitativa e market microstructure in una
base di conoscenza cercabile, accessibile direttamente da Cursor tramite MCP server.

---

## Cosa fa questo progetto

1. **Estrae testo** da 35 PDF (libri e paper accademici) in Markdown
2. **Taglia il testo** in chunk semantici con metadata (source, tipo, categoria, pagina)
3. **Indicizza i chunk** con embedding vettoriali (Google gemini-embedding-2) in ChromaDB
4. **Espone 3 tool MCP** che Cursor può chiamare per cercare informazioni nella knowledge base

Quando l'agente Cursor lavora su Vision, può cercare automaticamente nei manuali
la teoria corretta prima di implementare formule, pattern o strategie.

---

## Struttura del progetto

```
Vision/
├── .cursor/
│   ├── mcp.json                  # Configurazione MCP server per Cursor
│   └── rules/
│       ├── vision-knowledge.mdc  # Regole per uso knowledge base
│       └── vision-project.mdc    # Convenzioni progetto Vision
├── .env                          # API key Google (NON committare)
├── scripts/
│   ├── 01_extract_pdf.py         # Estrazione PDF → Markdown
│   ├── 02_chunk.py               # Chunking semantico con metadata
│   └── 03_index.py               # Embedding + indicizzazione ChromaDB
├── mcp_server/
│   └── server.py                 # MCP server (3 tool per Cursor)
├── docs/
│   ├── raw/                      # Markdown estratti dai PDF (generato)
│   ├── knowledge/                # Markdown puliti manualmente (futuro)
│   └── chunks/
│       └── all_chunks.json       # Chunk con metadata (generato)
├── vector_store/                 # ChromaDB persistent storage (generato)
├── requirements.txt              # Dipendenze Python
├── to_do_list.md                 # Prossimi passi e miglioramenti
└── README.md                     # Questo file
```

---

## Requisiti

- **Python 3.11+**
- **API key Google AI Studio** (per embedding gemini-embedding-2)

### Dipendenze Python

```
pymupdf >= 1.24.0        # Estrazione testo da PDF
chromadb >= 0.5.0         # Vector database locale
google-genai >= 2.0.0     # Google AI embedding
openai >= 1.30.0          # (opzionale, fallback embedding)
mcp[cli] >= 1.0.0         # MCP server framework
tiktoken >= 0.7.0         # Tokenizer per conteggio token
```

---

## Setup

### 1. Installare le dipendenze

```bash
pip install -r requirements.txt
```

### 2. Configurare la API key

Creare un file `.env` nella root del progetto:

```
GOOGLE_API_KEY=la-tua-chiave-google-ai-studio
```

### 3. Eseguire la pipeline

```bash
# Step 1: Estrai testo dai PDF
python scripts/01_extract_pdf.py

# Step 2: Chunking semantico
python scripts/02_chunk.py

# Step 3: Embedding e indicizzazione
python scripts/03_index.py
```

### 4. Configurare Cursor

Il file `.cursor/mcp.json` è già configurato. Dopo aver eseguito la pipeline:

1. Riavviare Cursor
2. Il tool `search_vision_docs` apparirà tra gli MCP disponibili
3. Le regole in `.cursor/rules/` guideranno l'agente nell'uso della knowledge base

---

## Pipeline — Dettaglio tecnico

### Step 1: Estrazione PDF (`01_extract_pdf.py`)

- **Input:** PDF da `C:\Users\Gabri\Strategy&Indicators\MATERIALERAGVISION`
- **Output:** file `.md` in `docs/raw/`, uno per PDF
- **Libreria:** PyMuPDF (pymupdf)
- **Formato output:** Markdown con frontmatter YAML (source_file, total_pages) e marcatori `<!-- PAGE N -->` per ogni pagina

**Statistiche attuali:**
- 35 PDF processati
- 32 con testo estratto (14.9 milioni di caratteri)
- 3 scansioni senza testo (Elliott Wave, Martin Pring, Options Volatility)

### Step 2: Chunking (`02_chunk.py`)

- **Input:** file `.md` da `docs/raw/`
- **Output:** `docs/chunks/all_chunks.json`
- **Strategia:** chunking semantico per sezione/paragrafo
- **Dimensione target:** 200–1200 token per chunk
- **Overlap:** ~100 token (tramite split di sezioni grandi)

Ogni chunk porta metadata:
| Campo | Descrizione |
|-------|-------------|
| `id` | Identificatore unico (filename + indice) |
| `source` | Nome del PDF originale |
| `source_type` | `"theory"` (libri) o `"spec"` (documenti Vision) |
| `categories` | Lista di tag tematici |
| `page` / `page_end` | Pagina/e nel PDF originale |
| `chunk_index` | Posizione nel documento |
| `tokens` | Conteggio token del chunk |

Il dizionario `BOOK_METADATA` nello script mappa i filename ai tag di categoria.

**Statistiche attuali:**
- 7857 chunk totali
- 3.7 milioni di token
- Media: 473 token/chunk

### Step 3: Indicizzazione (`03_index.py`)

- **Input:** `docs/chunks/all_chunks.json`
- **Output:** `vector_store/` (ChromaDB persistent)
- **Modello embedding:** Google `gemini-embedding-2` (3072 dimensioni)
- **Batch size:** 20 chunk per richiesta API
- **Distanza:** coseno
- **Fallback:** se `GOOGLE_API_KEY` non è presente, usa ChromaDB default (all-MiniLM-L6-v2)
- **Rate limiting:** retry automatico con pausa di 60s su errore 429

---

## MCP Server — Tool disponibili

Il server si trova in `mcp_server/server.py` e espone 3 tool:

### `search_vision_docs(query, n_results?, source_type?, category?)`

Ricerca semantica nella knowledge base. Tool principale.

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `query` | string | (obbligatorio) | Cosa cercare |
| `n_results` | int | 5 | Risultati da restituire (max 10) |
| `source_type` | string | "" | Filtro: `"theory"` o `"spec"` |
| `category` | string | "" | Filtro: `"formula"`, `"pattern"`, `"strategy"`, ecc. |

**Esempio:** `search_vision_docs("Wyckoff Spring accumulation", source_type="theory")`

### `get_module_spec(source_name, max_chunks?)`

Recupera tutti i chunk di un documento specifico, ordinati per pagina.

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `source_name` | string | (obbligatorio) | Parte del nome file (es. "wyckoff", "murphy") |
| `max_chunks` | int | 20 | Massimo chunk da restituire |

### `list_sources()`

Elenca tutte le fonti disponibili con conteggio chunk e categorie. Nessun parametro.

---

## Fonti indicizzate (32 documenti)

| Fonte | Chunk | Categorie |
|-------|-------|-----------|
| Wyckoff Methodology in Depth (x2) | 288 | pattern, strategy, methodology |
| Wyckoff 2.0 Structures, Volume Profile | 216 | pattern, strategy, methodology |
| Anna Coulling — Volume Price Analysis | 59 | volume, price_action |
| De Prado — Advances in Financial ML | 158 | formula, machine_learning, quantitative |
| Murphy — Technical Analysis of Financial Markets | 408 | technical_analysis |
| Pring — Technical Analysis Explained | 673 | momentum, technical_analysis |
| Ernest Chan — Algorithmic Trading + Quantitative Trading | 387 | algorithmic_trading, quantitative |
| Aronson — Evidence-Based Technical Analysis | 510 | evidence_based, technical_analysis |
| Adam Grimes — Art and Science of Technical Analysis | 443 | market_structure, price_action |
| Dalton — Mind over Markets | 199 | market_profile, volume |
| Profit with the Market Profile | 211 | market_profile, volume |
| Trading Systems and Methods | 1566 | strategy, systematic |
| Algorithmic and High-Frequency Trading | 342 | algorithmic_trading, hft |
| Avellaneda & Stoikov — Limit Order Book | 14 | market_microstructure |
| The Price Impact of Order Book Events | 40 | market_microstructure |
| Trading Exchanges — Market Microstructure | 105 | market_microstructure |
| Sinclair — Volatility Trading | 72 | volatility, options |
| Machine Learning for Algorithmic Trading | 241 | machine_learning |
| Reinforcement Learning (Sutton & Barto) | 535 | machine_learning |
| N-BEATS Neural Expansion Analysis | 36 | machine_learning, time_series |
| Temporal Fusion Transformers | 26 | machine_learning, time_series |
| Portfolio Mathematics Handbook | 434 | portfolio, risk |
| Active Portfolio Management | 31 | portfolio, risk |
| Pedersen — Efficiently Inefficient | 63 | quantitative |
| Flash Boys | 49 | market_microstructure |
| Guide italiane (Analisi Tecnica + Trading) | 681 | technical_analysis, strategy |
| SSRN-1695596 | 70 | — |

**Non indicizzati (scansioni, serve OCR):**
- Elliott Wave Principle (Frost & Prechter)
- Martin Pring — Market Momentum
- Options, Volatility and Pricing (Sheldon Natenberg)

---

## Risultati dei test

Test eseguiti il 12/05/2026 con 7 query rappresentative:

| Query | Relevance top-1 | Fonte trovata | Valutazione |
|-------|-----------------|---------------|-------------|
| Wyckoff accumulation Spring SOS LPS | 0.821 | Wyckoff Methodology in Depth | Eccellente |
| Volume analysis institutional activity | 0.759 | Wyckoff + Wyckoff 2.0 | Buono |
| Order book imbalance formula | 0.770 | Price Impact of Order Book Events | Buono |
| VWAP calculation | 0.749 | Trading Systems and Methods | Buono |
| Limit order book bid ask spread | 0.784 | Avellaneda & Stoikov | Buono |
| ML for price prediction (filtro category) | — | Nessun risultato | Da correggere (metadata) |

---

## Come rilanciare la pipeline

Dopo modifiche ai metadata, al chunking o aggiunta di nuovi PDF:

```bash
# Solo re-chunk + re-index (se i PDF non cambiano)
python scripts/02_chunk.py
python scripts/03_index.py

# Pipeline completa (se aggiungi nuovi PDF)
python scripts/01_extract_pdf.py
python scripts/02_chunk.py
python scripts/03_index.py
```

Tempo stimato: ~10 minuti per la pipeline completa (di cui ~6 min per l'indicizzazione Google).

---

## Prossimi passi

Vedi `to_do_list.md` per la lista completa e prioritizzata.
