# Vision — Knowledge Base & RAG Pipeline

Sistema di knowledge base per il progetto **Vision** (monitoraggio crypto e stock).
Trasforma manuali di trading, finanza quantitativa e market microstructure in una
base di conoscenza cercabile, accessibile da Cursor tramite MCP server.

**Stato (maggio 2026):** 36 fonti nei chunk, **8868** chunk in `all_chunks.json`, circa **4,44M** token (media ~501 token/chunk). In ChromaDB vengono indicizzati i chunk con almeno **120** token (i frammenti più piccoli vengono saltati per non inquinare la ricerca). Embedding predefinito: **Google `gemini-embedding-2`** (3072 dimensioni).

---

## Cosa fa questo progetto

1. **Estrae testo** dai PDF nella cartella sorgente in Markdown (`docs/raw/`) — estrazione nativa con PyMuPDF; per scansioni senza testo selezionabile, script dedicato **OCR** (Tesseract + PyMuPDF).
2. **Taglia il testo** in chunk con confini il più possibile allineati alle frasi, con metadata (source, tipo, categoria, pagina).
3. **Indicizza i chunk** in ChromaDB con embedding vettoriali.
4. **Espone 3 tool MCP** che Cursor può chiamare per interrogare la knowledge base.

Quando l’agente Cursor lavora su Vision, può cercare nei manuali la teoria corretta prima di implementare formule, pattern o strategie.

---

## Struttura del progetto

```
Vision/
├── .cursor/
│   ├── mcp.json                  # Configurazione MCP server per Cursor
│   └── rules/
│       ├── vision-knowledge.mdc  # Regole per uso knowledge base
│       └── vision-project.mdc    # Convenzioni progetto Vision (stato corpus)
├── .env                          # GOOGLE_API_KEY (non committare)
├── scripts/
│   ├── 01_extract_pdf.py         # Estrazione PDF → Markdown (testo nativo)
│   ├── 01_extract_pdf_ocr.py     # OCR per PDF scannerizzati (Tesseract)
│   ├── 02_chunk.py               # Chunking con tiktoken (300–1200 token)
│   ├── 03_index.py               # Embedding + ChromaDB (resume, --fresh)
│   ├── chunk_quality_audit.py    # Audit qualità chunk (legacy)
│   └── chunk_quality_audit_v2.py # Audit qualità RAG (usato per il report)
├── mcp_server/
│   └── server.py                 # MCP server (FastMCP, 3 tool)
├── docs/
│   ├── raw/                      # Markdown estratti (generato)
│   ├── knowledge/                # Markdown puliti / strutturati (manuale, opzionale)
│   ├── chunks/
│   │   └── all_chunks.json       # Chunk con metadata (generato)
│   ├── RAG_report.md             # Report RAG + audit (query, trend vs baseline)
│   └── chunk_quality_baseline.json
├── vector_store/                 # ChromaDB (generato, in genere gitignored)
├── src/                          # Codice applicativo Vision (da sviluppare)
├── requirements.txt
├── Ideas.txt                     # Note e idee di prodotto
└── README.md
```

---

## Requisiti

- **Python 3.11+**
- **API key Google AI Studio** (`GOOGLE_API_KEY`) per embedding `gemini-embedding-2` (stesso stack della pipeline e del MCP, se non usi fallback locale).
- **Solo per OCR:** [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installato sul sistema (su Windows, ad es. `winget install UB-Mannheim.TesseractOCR`). Vedi commenti in cima a `scripts/01_extract_pdf_ocr.py` per `TESSDATA_PREFIX` e DPI.

### Dipendenze Python (`requirements.txt`)

```
pymupdf>=1.24.0        # Estrazione testo / rendering pagine per OCR
chromadb>=0.5.0        # Vector database locale
google-genai>=2.0.0  # Client Google per embedding
openai>=1.30.0         # Opzionale / compatibilità
mcp[cli]>=1.0.0        # Framework MCP server
tiktoken>=0.7.0        # Conteggio token (cl100k_base)
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

Per sviluppo senza chiave Google, la pipeline di indicizzazione può usare embedding locali: impostare `USE_LOCAL=1` nell’ambiente prima di `03_index.py` (vedi docstring dello script). Il server MCP, se la chiave manca o è segnaposto, non userà gli stessi embedding di produzione: per ricerca coerente con l’indice Google serve la chiave configurata.

### 3. Eseguire la pipeline

```bash
# Step 1a: PDF con testo selezionabile
python scripts/01_extract_pdf.py

# Step 1b (solo scansioni): OCR sui PDF predefiniti in MATERIALERAGVISION
python scripts/01_extract_pdf_ocr.py

# Step 2: Chunking
python scripts/02_chunk.py

# Step 3: Embedding e indicizzazione (resume se la collection esiste già)
python scripts/03_index.py

# Re-indicizzazione completa da zero
python scripts/03_index.py --fresh
```

### 4. Configurare Cursor

Il file `.cursor/mcp.json` punta al server in `mcp_server/server.py`. Dopo aver costruito `vector_store/`:

1. Riavviare Cursor se necessario.
2. I tool MCP (`search_vision_docs`, `get_module_spec`, `list_sources`) compaiono tra le risorse configurate.
3. Le regole in `.cursor/rules/` guidano l’agente sull’uso della knowledge base e sulle lacune note del corpus.

---

## Pipeline — Dettaglio tecnico

### Step 1: Estrazione (`01_extract_pdf.py` / `01_extract_pdf_ocr.py`)

- **Input PDF:** cartella `C:\Users\Gabri\Strategy&Indicators\MATERIALERAGVISION` (percorsi fissi negli script; adattare se serve portabilità).
- **Output:** file `.md` in `docs/raw/`, con frontmatter YAML e marcatori `<!-- PAGE N -->` dove applicabile.
- **OCR:** `01_extract_pdf_ocr.py` è pensato per i PDF senza layer di testo (Elliott Wave, Pring Momentum, Natenberg, ecc.); supporta DPI configurabile e modalità a doppia colonna per ridurre l’interleaving del testo.

### Step 2: Chunking (`02_chunk.py`)

- **Input:** `docs/raw/*.md`
- **Output:** `docs/chunks/all_chunks.json`
- **Parametri principali:** `MIN_CHUNK_TOKENS=300`, `MAX_CHUNK_TOKENS=1200`, `OVERLAP_TOKENS=80`, tokenizer `cl100k_base`; split e merge **consapevoli della frase** (con conteggio token rigoroso sul testo unito).
- **Metadata:** mappatura `BOOK_METADATA` per `source_type`, `categories` e regole speciali (es. scarto di primi chunk rumorosi su alcuni stem OCR).

Campi tipici per chunk:

| Campo | Descrizione |
|-------|-------------|
| `id` | Identificatore univoco |
| `source` | Nome file PDF di riferimento |
| `source_type` | `"theory"` o `"spec"` |
| `categories` | Tag tematici |
| `page` / `page_end` | Pagina nel documento |
| `chunk_index` | Ordine nel documento |
| `tokens` | Token stimati |

### Step 3: Indicizzazione (`03_index.py`)

- **Input:** `docs/chunks/all_chunks.json`
- **Output:** `vector_store/` (persistente)
- **Modello:** `gemini-embedding-2`; distanza coseno; batch 20; retry con backoff su errori transitori (rate limit, 5xx).
- **Filtro:** chunk con `tokens < 120` non vengono indicizzati.
- **Resume:** se la collection esiste, vengono aggiunti solo i chunk mancanti; `--fresh` ricrea l’indice da zero.

---

## Qualità RAG e audit

- **`scripts/chunk_quality_audit_v2.py`** — analisi euristiche sui chunk (es. inizio/fine a metà frase).
- **`docs/RAG_report.md`** — sintesi del comportamento del sistema e confronto con `docs/chunk_quality_baseline.json`.
- Dopo cambiamenti massicci a `docs/raw/`, metadata o logica di chunking: rilanciare audit e aggiornare il report se mantieni una baseline tracciata.

---

## MCP Server — Tool disponibili

Server: `mcp_server/server.py` (FastMCP). Tre tool:

### `search_vision_docs(query, n_results?, source_type?, category?)`

Ricerca semantica. Parametri principali: `query` (obbligatorio), `n_results` (default 5, max 10), filtri opzionali `source_type` e `category`.

### `get_module_spec(source_name, max_chunks?)`

Chunk di un documento, ordinati per pagina; `source_name` è una sottostringa del nome file.

### `list_sources()`

Elenco fonti con conteggi e categorie — utile per avere lo stato aggiornato senza duplicare tabelle nel README.

---

## Fonti e corpus

Il corpus include manuali classici (Wyckoff, Murphy, Pring, microstructure, ML per il trading, opzioni, ecc.), paper (es. flow toxicity / VPIN su SSRN), guide in italiano e più titoli su algoritmic trading e HFT. **Elliott Wave, Pring on Momentum e Natenberg** provengono da scansioni con OCR: sono indicizzati ma il testo può contenere errori; conviene incrociare con altre fonti quando serve precisione assoluta.

Per elenco e conteggi aggiornati: tool MCP **`list_sources()`** oppure ispezione di `all_chunks.json`.

---

## Risultati dei test (storici)

Nel README del 12/05/2026 erano documentate query manuali su ricerca semantica (Wyckoff, order book, VWAP, ecc.) con score di rilevanza. Per esiti aggiornati, query aggiuntive e metriche di audit, fare riferimento a **`docs/RAG_report.md`**.

---

## Come rilanciare la pipeline

```bash
# Solo re-chunk + re-index (PDF invariati)
python scripts/02_chunk.py
python scripts/03_index.py

# Pipeline completa (nuovi PDF o re-estrazione)
python scripts/01_extract_pdf.py
python scripts/01_extract_pdf_ocr.py   # se servono scansioni
python scripts/02_chunk.py
python scripts/03_index.py
```

Indice pulito da zero: `python scripts/03_index.py --fresh`.

Tempo indicativo: dipende dal volume e dai limiti API; l’embedding Google è la fase più lenta.

---

## Prossimi passi

Note operative e idee: **`Ideas.txt`**. Convenzioni e stato del corpus (abbreviazioni, lacune tipo CVD non coperto dai libri, principi “theory before code”): **`.cursor/rules/vision-project.mdc`**.

Non committare `.env`, chiavi API o blob di `vector_store/`; rigenerare l’indice dagli script quando si condivide il repo o si apre una PR.
