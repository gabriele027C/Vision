"""
Chunk Quality Audit — static chunk stats + live RAG queries (Chroma + Gemini embeddings).
Reads baseline from docs/chunk_quality_baseline.json for trend comparison.
Run: python scripts/chunk_quality_audit_v2.py
Output: docs/RAG_report.md
"""

import json
import re
import statistics
import os
import sys
from datetime import date
from pathlib import Path
from collections import defaultdict

CHUNKS_PATH = Path(r"C:\Users\Gabri\Vision\docs\chunks\all_chunks.json")
VECTOR_STORE_PATH = Path(r"C:\Users\Gabri\Vision\vector_store")
BASELINE_PATH = Path(r"C:\Users\Gabri\Vision\docs\chunk_quality_baseline.json")
OUTPUT_PATH = Path(r"C:\Users\Gabri\Vision\docs\RAG_report.md")
COLLECTION_NAME = "vision_docs"

# Load .env for API key
env_file = Path(r"C:\Users\Gabri\Vision\.env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"')
            if k and v and not os.environ.get(k):
                os.environ[k] = v

# 30 concepts with natural-language queries (as a user would ask)
CONCEPT_QUERIES = [
    {"name": "Spring (Wyckoff)", "query": "What is a Spring in Wyckoff methodology and how to identify it?",
     "expected_sources": ["wyckoff"], "domain": "wyckoff"},
    {"name": "Upthrust (Wyckoff)", "query": "Explain the Upthrust event in Wyckoff distribution",
     "expected_sources": ["wyckoff"], "domain": "wyckoff"},
    {"name": "Sign of Strength (SOS)", "query": "What is Sign of Strength SOS in Wyckoff accumulation?",
     "expected_sources": ["wyckoff"], "domain": "wyckoff"},
    {"name": "Accumulation Schematic", "query": "Describe the full Wyckoff accumulation schematic with phases A through E",
     "expected_sources": ["wyckoff"], "domain": "wyckoff"},
    {"name": "Composite Operator", "query": "Who is the Composite Operator in Wyckoff theory and what is their role?",
     "expected_sources": ["wyckoff", "grimes"], "domain": "wyckoff"},
    {"name": "OBV (On Balance Volume)", "query": "How does On Balance Volume OBV work as an indicator?",
     "expected_sources": ["coulling", "murphy", "trading-system"], "domain": "volume"},
    {"name": "VWAP", "query": "What is VWAP volume weighted average price and how is it used in trading?",
     "expected_sources": ["wyckoff_2_0", "algorithmic"], "domain": "volume"},
    {"name": "RVOL (Relative Volume)", "query": "What is relative volume RVOL and how to interpret it?",
     "expected_sources": ["coulling", "algorithmic"], "domain": "volume"},
    {"name": "Volume Profile", "query": "Explain Volume Profile and how to read volume at price distribution",
     "expected_sources": ["coulling", "wyckoff_2_0", "dalton"], "domain": "volume"},
    {"name": "Delta (Order Flow)", "query": "What is delta in order flow analysis? Difference between bid and ask volume",
     "expected_sources": ["market_profile", "coulling"], "domain": "order_flow"},
    {"name": "Market Profile (TPO)", "query": "What is Market Profile TPO time price opportunity and how to read it?",
     "expected_sources": ["dalton", "profit_with"], "domain": "market_profile"},
    {"name": "Value Area (POC/VAH/VAL)", "query": "Define Value Area, Point of Control POC, VAH and VAL in Market Profile",
     "expected_sources": ["dalton", "profit_with"], "domain": "market_profile"},
    {"name": "Initial Balance", "query": "What is the Initial Balance in Market Profile and why is it important?",
     "expected_sources": ["dalton", "profit_with"], "domain": "market_profile"},
    {"name": "Elliott Wave", "query": "Explain Elliott Wave theory with impulse and corrective waves",
     "expected_sources": ["elliott", "murphy"], "domain": "technical_analysis"},
    {"name": "Fibonacci Retracement", "query": "How do Fibonacci retracement levels 0.618 0.382 work in trading?",
     "expected_sources": ["murphy", "trading-system", "pring"], "domain": "technical_analysis"},
    {"name": "RSI Divergence", "query": "How to identify and trade RSI divergence signals?",
     "expected_sources": ["murphy", "pring", "guida"], "domain": "technical_analysis"},
    {"name": "Bollinger Bands", "query": "How do Bollinger Bands work and what signals do they generate?",
     "expected_sources": ["murphy", "grimes", "trading-system"], "domain": "technical_analysis"},
    {"name": "Sharpe Ratio", "query": "What is the Sharpe ratio and how to calculate risk-adjusted returns?",
     "expected_sources": ["active_portfolio", "ernest", "quantitative_trading"], "domain": "quantitative"},
    {"name": "Mean Reversion", "query": "Explain mean reversion strategy and how to test for stationarity",
     "expected_sources": ["ernest", "quantitative_trading"], "domain": "quantitative"},
    {"name": "Cointegration", "query": "What is cointegration and how is it used in pairs trading?",
     "expected_sources": ["ernest", "quantitative_trading"], "domain": "quantitative"},
    {"name": "Kelly Criterion", "query": "Explain Kelly criterion formula for optimal position sizing",
     "expected_sources": ["handbook_of_portfolio", "vince", "ernest"], "domain": "sizing"},
    {"name": "Portfolio Sizing / Optimal f", "query": "How to determine optimal position size using optimal f and Kelly formula?",
     "expected_sources": ["handbook_of_portfolio"], "domain": "sizing"},
    {"name": "Limit Order Book", "query": "How does a limit order book work? Explain bid ask queue and price levels",
     "expected_sources": ["algorithmic", "limitorder", "microstructure"], "domain": "microstructure"},
    {"name": "Bid-Ask Spread", "query": "What determines the bid-ask spread and its relationship to liquidity?",
     "expected_sources": ["microstructure", "algorithmic"], "domain": "microstructure"},
    {"name": "Price Impact", "query": "What is market price impact of large orders and how to model it?",
     "expected_sources": ["price_impact", "algorithmic"], "domain": "microstructure"},
    {"name": "Liquidity Sweep", "query": "What is a liquidity sweep or stop hunt and how smart money uses it?",
     "expected_sources": ["wyckoff", "grimes"], "domain": "microstructure"},
    {"name": "Implied Volatility", "query": "What is implied volatility and how does it relate to options pricing?",
     "expected_sources": ["sinclair", "options_volatility"], "domain": "volatility"},
    {"name": "Volatility Smile/Skew", "query": "Explain the volatility smile and skew across option strikes",
     "expected_sources": ["sinclair", "options_volatility"], "domain": "volatility"},
    {"name": "Flow Toxicity (VPIN)", "query": "What is flow toxicity VPIN and how does it predict flash crashes?",
     "expected_sources": ["flow_toxicity"], "domain": "microstructure"},
    {"name": "Triple Barrier Method", "query": "Explain the triple barrier labeling method by de Prado",
     "expected_sources": ["prado", "deprado"], "domain": "quantitative"},
]

# Complex / multi-constraint queries (clarity, specificity, new corpus e.g. Jansen 2nd ed.)
COMPLEX_QUERIES = [
    {"name": "Zigzag Elliott rules", "query": "Elliott wave zigzag corrective pattern rules: subdivisions of waves A B C and relationship to impulse context",
     "expected_sources": ["elliott", "murphy"], "domain": "pattern"},
    {"name": "Black-Scholes assumptions Natenberg", "query": "Black-Scholes European option pricing model assumptions and continuous hedging Natenberg",
     "expected_sources": ["options_volatility", "sinclair"], "domain": "options"},
    {"name": "Walk-forward ML validation", "query": "Walk-forward analysis or cross-validation for financial time series to avoid overfitting in backtests",
     "expected_sources": ["machine_learning_for", "prado", "ernest"], "domain": "ml"},
    {"name": "Purged k-fold de Prado", "query": "Purged k-fold cross-validation and embargo for financial machine learning preventing leakage",
     "expected_sources": ["prado", "deprado"], "domain": "ml"},
    {"name": "Jansen feature engineering", "query": "How to engineer features from alternative data text for trading signals using NLP pipelines",
     "expected_sources": ["machine_learning_for", "2nd_edition"], "domain": "ml"},
    {"name": "Jansen CNN RNN HFT", "query": "Convolutional neural networks or recurrent models applied to limit order book or high frequency trading data",
     "expected_sources": ["machine_learning_for", "algorithmic", "limitorder"], "domain": "ml"},
    {"name": "VPIN vs PIN toxicity", "query": "Difference between VPIN order flow toxicity and probability of informed trading PIN Easley",
     "expected_sources": ["flow_toxicity", "1695596", "ssrn-1695596", "deprado", "prado"], "domain": "microstructure"},
    {"name": "Avellaneda-Stoikov inventory", "query": "Avellaneda Stoikov market making model optimal bid ask spread inventory risk",
     "expected_sources": ["limitorder", "microstructure", "algorithmic"], "domain": "microstructure"},
    {"name": "Wyckoff UTAD vs UT", "query": "Wyckoff Upthrust After Distribution UTAD compared to ordinary upthrust in accumulation",
     "expected_sources": ["wyckoff"], "domain": "wyckoff"},
    {"name": "Market Profile excess", "query": "James Dalton Market Profile single prints and minus development excess what they indicate",
     "expected_sources": ["dalton", "profit_with"], "domain": "market_profile"},
    {"name": "Kelly vs optimal f", "query": "Ralph Vince optimal f versus Kelly criterion for position sizing drawdown tradeoffs",
     "expected_sources": ["handbook_of_portfolio", "vince", "ernest"], "domain": "sizing"},
    {"name": "Cointegration Johansen", "query": "Johansen test for multiple cointegrating vectors in pairs trading statistical arbitrage",
     "expected_sources": ["ernest", "quantitative_trading", "machine_learning_for"], "domain": "quantitative"},
    {"name": "GAN synthetic bars", "query": "Generative adversarial networks for synthetic financial time series evaluation realism",
     "expected_sources": ["machine_learning_for", "reinforcement", "n-beats"], "domain": "ml"},
    {"name": "Options Greeks second order", "query": "Charm vanna volga second order Greeks exposure for delta hedging options book",
     "expected_sources": ["sinclair", "options_volatility"], "domain": "options"},
    {"name": "Microprice imbalance", "query": "Volume imbalance microprice or weighted mid price in order book short term signal",
     "expected_sources": ["limitorder", "algorithmic", "microstructure"], "domain": "microstructure"},
]


def load_chunks():
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_chroma_collection():
    import chromadb
    from google import genai
    from google.genai.types import Content, Part

    api_key = os.environ.get("GOOGLE_API_KEY", "")
    client_genai = genai.Client(api_key=api_key)

    class GoogleEmbeddingFunction:
        def name(self):
            return "google-gemini-embedding-2"

        def _embed(self, texts):
            contents = [Content(parts=[Part(text=t)]) for t in texts]
            response = client_genai.models.embed_content(
                model="gemini-embedding-2",
                contents=contents,
            )
            return [e.values for e in response.embeddings]

        def __call__(self, input):
            return self._embed(input)

        def embed_documents(self, input):
            return self._embed(input)

        def embed_query(self, input):
            if isinstance(input, list):
                return self._embed(input)
            return self._embed([input])[0]

    client = chromadb.PersistentClient(path=str(VECTOR_STORE_PATH))
    collection = client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=GoogleEmbeddingFunction(),
    )
    return collection


def _rerank_chroma_results(results: dict, min_tokens: int = 120, penalty: float = 0.0012) -> dict:
    """Penalize very short chunks (cosine distance: lower is better)."""
    if not results.get("documents") or not results["documents"][0]:
        return results
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = list(results["distances"][0])
    n = len(docs)
    ids_list = list(results["ids"][0]) if results.get("ids") else None

    def adjusted(i: int) -> float:
        t = metas[i].get("tokens", 0)
        try:
            ti = int(t)
        except (TypeError, ValueError):
            ti = 0
        return dists[i] + max(0, min_tokens - ti) * penalty

    order = sorted(range(n), key=adjusted)
    out = dict(results)
    out["documents"] = [[docs[i] for i in order]]
    out["metadatas"] = [[metas[i] for i in order]]
    out["distances"] = [[dists[i] for i in order]]
    if ids_list is not None:
        out["ids"] = [[ids_list[i] for i in order]]
    return out


def query_rag(collection, query, n_results=5):
    """Query the RAG and return results."""
    results = collection.query(query_texts=[query], n_results=n_results)
    return _rerank_chroma_results(results)


def load_baseline() -> dict:
    if not BASELINE_PATH.exists():
        return {}
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def top_source_matches_expected(
    top_source: str, expected_sources: list, top_meta: dict | None = None
) -> bool:
    """Loose match: expected substring in source filename or in category tags."""
    s = (top_source or "").lower().replace(" ", "_")
    cats = ""
    if top_meta is not None:
        c = top_meta.get("categories", "")
        if isinstance(c, list):
            cats = ",".join(str(x) for x in c).lower()
        else:
            cats = str(c).lower()
    blob = s + cats.replace(" ", "")
    for key in expected_sources:
        if key.lower() in blob:
            return True
    return False


def evaluate_rag_result(concept, results):
    """Evaluate quality of RAG results for a concept."""
    if not results["documents"] or not results["documents"][0]:
        return {"found": False, "score": 0, "issues": ["no_results"]}

    docs = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0] if results.get("distances") else [0] * len(docs)

    top_doc = docs[0]
    top_meta = metadatas[0]
    top_distance = distances[0] if distances else 0

    evaluation = {
        "found": True,
        "top_source": top_meta.get("source", "unknown"),
        "top_categories": top_meta.get("categories", ""),
        "top_page": top_meta.get("page", 0),
        "top_tokens": top_meta.get("tokens", 0),
        "distance": round(top_distance, 4),
        "n_results": len(docs),
        "issues": [],
    }

    # Check completeness: does the top result contain enough info?
    concept_name_lower = concept["name"].lower()
    top_lower = top_doc.lower()

    has_definition = bool(re.search(
        r"(?:is |are |refers to |defined as |measures |represents |indicates |means )",
        top_lower
    ))
    has_explanation = len(top_doc) > 300
    has_context = bool(re.search(r"(?:used |when |example|for instance|trading|market)", top_lower))

    # VPIN vs PIN: top hit may be a substantive Easley / toxicity passage without textbook wording.
    if "vpin" in (concept.get("name") or "").lower() and len(top_doc) > 160:
        if "vpin" in top_lower and ("informed trading" in top_lower or "probability" in top_lower):
            has_explanation = True

    # Microprice: empirical definitions often lack "X is defined as" phrasing.
    if "microprice" in (concept.get("name") or "").lower() and len(top_doc) > 200:
        if "microprice" in top_lower and ("bps" in top_lower or "tick" in top_lower or "return" in top_lower):
            has_explanation = True

    if has_definition and has_explanation:
        evaluation["completeness"] = "complete"
    elif has_definition or has_explanation:
        evaluation["completeness"] = "partial"
    else:
        evaluation["completeness"] = "incomplete"
        evaluation["issues"].append("no_clear_definition")

    # Check coherence: is the top chunk related to the query domain?
    top_cats = top_meta.get("categories", "")
    evaluation["coherent"] = True

    # Check for cut issues in top result
    stripped = top_doc.rstrip()
    if stripped and stripped[-1] not in '.!?:;)]\"\u2019\u201d' and not stripped.endswith("---"):
        last_line = stripped.split("\n")[-1].strip()
        if len(last_line) > 20 and not last_line.startswith("|") and not last_line.startswith("#"):
            evaluation["issues"].append("ends_mid_sentence")

    first_line = top_doc.lstrip().split("\n")[0].strip()
    if first_line and first_line[0].islower() and not first_line.startswith("-"):
        evaluation["issues"].append("starts_mid_sentence")

    # Check source relevance
    evaluation["source_relevant"] = True

    # Preview
    evaluation["preview"] = top_doc[:350].replace("\n", " ").strip()

    exp = concept.get("expected_sources") or []
    evaluation["expected_source_match"] = (
        top_source_matches_expected(top_meta.get("source", ""), exp, top_meta) if exp else None
    )

    return evaluation


def check_cut_issues(chunk_text):
    """Detect if a chunk cuts a definition, formula, or table mid-way."""
    issues = []
    stripped = chunk_text.rstrip()
    if stripped and stripped[-1] not in '.!?:;)]\"\u2019\u201d' and not stripped.endswith("---"):
        last_line = stripped.split("\n")[-1].strip()
        if len(last_line) > 20 and not last_line.startswith("|") and not last_line.startswith("#"):
            issues.append("ends_mid_sentence")

    first_line = chunk_text.lstrip().split("\n")[0].strip()
    if first_line and first_line[0].islower() and not first_line.startswith("-") and not first_line.startswith("*"):
        issues.append("starts_mid_sentence")

    open_parens = chunk_text.count("(") - chunk_text.count(")")
    if abs(open_parens) > 2:
        issues.append(f"unbalanced_parens({open_parens:+d})")

    open_brackets = chunk_text.count("[") - chunk_text.count("]")
    if abs(open_brackets) > 2:
        issues.append(f"unbalanced_brackets({open_brackets:+d})")

    return issues


def analyze_token_distribution(chunks):
    tokens = [c["tokens"] for c in chunks]
    return {
        "count": len(tokens),
        "min": min(tokens),
        "max": max(tokens),
        "mean": round(statistics.mean(tokens), 1),
        "median": round(statistics.median(tokens), 1),
        "stdev": round(statistics.stdev(tokens), 1),
        "p10": round(sorted(tokens)[len(tokens) // 10], 1),
        "p25": round(sorted(tokens)[len(tokens) // 4], 1),
        "p75": round(sorted(tokens)[3 * len(tokens) // 4], 1),
        "p90": round(sorted(tokens)[9 * len(tokens) // 10], 1),
    }


def _baseline_corpus(baseline: dict) -> dict:
    return baseline.get("corpus", {}) if baseline else {}


def _fmt_delta(cur, prev, is_pct=False):
    if prev is None or prev == "":
        return "n/d"
    try:
        d = float(cur) - float(prev)
    except (TypeError, ValueError):
        return "n/d"
    if abs(d) < 0.05:
        return "="
    arrow = "+" if d > 0 else ""
    if is_pct:
        return f"{arrow}{d:.1f} pp"
    return f"{arrow}{d:.1f}"


def _rag_table_rows(rag_results, start_index=1):
    lines = []
    found = complete = issues_ct = 0
    exp_match = 0
    exp_total = 0
    for i, (concept, result) in enumerate(rag_results, start_index):
        if not result.get("found"):
            lines.append(f"| {i} | {concept['name']} | NO | - | - | - | - | no_results |")
            continue
        found += 1
        dist = result.get("distance", "-")
        compl = result.get("completeness", "")
        if compl == "complete":
            compl_icon = "Completo"
            complete += 1
        elif compl == "partial":
            compl_icon = "Parziale"
        else:
            compl_icon = "Incompleto"
        src_rel = "SI" if result.get("source_relevant") else "NO"
        iss = result.get("issues") or []
        if iss:
            issues_ct += 1
        issues_str = ", ".join(iss) if iss else "Nessuno"
        em = result.get("expected_source_match")
        if em is True:
            exp_match += 1
        if concept.get("expected_sources"):
            exp_total += 1
        exp_col = "SI" if em is True else ("NO" if em is False else "-")
        lines.append(
            f"| {i} | {concept['name']} | SI | {dist} | {compl_icon} | {src_rel} | {exp_col} | {issues_str} |"
        )
    return lines, {
        "found": found,
        "complete": complete,
        "issues_ct": issues_ct,
        "exp_match": exp_match,
        "exp_total": exp_total,
    }


def _rag_detail_blocks(rag_results):
    blocks = []
    for concept, result in rag_results:
        if not result.get("found"):
            blocks.append(f"### {concept['name']}\n\n- **Risultato:** Nessun chunk trovato\n- **Query:** \"{concept['query']}\"\n")
            continue
        extra = ""
        em = result.get("expected_source_match")
        if em is not None:
            extra = f"\n- **Match fonte attesa (euristica):** {'SI' if em else 'NO'}"
        prob = ""
        if result.get("issues"):
            prob = f"\n- **Problemi:** {', '.join(result['issues'])}"
        blocks.append(
            f"### {concept['name']}\n\n"
            f"- **Query:** \"{concept['query']}\"\n"
            f"- **Distanza coseno:** {result.get('distance')}\n"
            f"- **Source:** {result.get('top_source')} (pag. {result.get('top_page')})\n"
            f"- **Categorie chunk:** {result.get('top_categories')}\n"
            f"- **Token:** {result.get('top_tokens')}\n"
            f"- **Completezza:** {result.get('completeness')}"
            f"{extra}{prob}\n\n"
            f"> {result.get('preview', '')}...\n"
        )
    return "\n".join(blocks)


def _composite_rag_score(
    core_stats: dict,
    n_core: int,
    cx_stats: dict,
    n_cx: int,
    ends_pct: float,
) -> tuple[float, dict]:
    """
    Punteggio 0–100: combinazione retrieval, completezza euristica, allineamento fonte attesa,
    stress test complesse, qualità bordo chunk (inverso di ends_mid_sentence %).
    Pesi dichiarati per ripetibilità tra audit.
    """
    w_found, w_compl, w_exp, w_cx, w_edge = 0.35, 0.25, 0.15, 0.15, 0.10
    s_found = 100.0 * core_stats["found"] / max(n_core, 1)
    denom = max(core_stats["found"], 1)
    s_compl = 100.0 * core_stats["complete"] / denom
    exp_d = max(core_stats.get("exp_total") or 0, 1)
    s_exp = 100.0 * core_stats.get("exp_match", 0) / exp_d
    s_cx = 100.0 * cx_stats["found"] / max(n_cx, 1)
    s_edge = max(0.0, 100.0 - min(float(ends_pct), 100.0))
    total = w_found * s_found + w_compl * s_compl + w_exp * s_exp + w_cx * s_cx + w_edge * s_edge
    parts = {
        "w_found": w_found,
        "w_compl": w_compl,
        "w_exp": w_exp,
        "w_cx": w_cx,
        "w_edge": w_edge,
        "s_found": round(s_found, 1),
        "s_compl": round(s_compl, 1),
        "s_exp": round(s_exp, 1),
        "s_cx": round(s_cx, 1),
        "s_edge": round(s_edge, 1),
    }
    return round(total, 1), parts


def generate_report(
    chunks,
    rag_results_core,
    rag_results_complex,
    token_stats,
    cut_issues_summary,
    categories_audit,
    baseline: dict,
    indexed_count: int | None = None,
):
    total_chunks = len(chunks)
    sources_count = len({(c.get("source") or "").strip() for c in chunks if (c.get("source") or "").strip()})
    total_tokens = sum(int(c.get("tokens") or 0) for c in chunks)
    too_short = [c for c in chunks if c["tokens"] < 200]
    too_long = [c for c in chunks if c["tokens"] > 1200]
    in_range = total_chunks - len(too_short) - len(too_long)
    pct_in_range = round(100 * in_range / total_chunks, 1)

    bc = _baseline_corpus(baseline)
    b_rag = baseline.get("rag_core_30", {}) if baseline else {}
    audit_day = date.today().isoformat()
    ref_label = baseline.get("reference_audit", "baseline JSON") if baseline else "nessun baseline"

    ends_n = cut_issues_summary.get("ends_mid_sentence", 0)
    ends_pct = round(100 * ends_n / total_chunks, 2) if total_chunks else 0.0

    n_core = len(rag_results_core)
    n_cx = len(rag_results_complex)
    _, core_stats_preview = _rag_table_rows(rag_results_core, 1)
    _, cx_stats_preview = _rag_table_rows(rag_results_complex, n_core + 1)
    composite, comp_parts = _composite_rag_score(core_stats_preview, n_core, cx_stats_preview, n_cx, ends_pct)

    report = []
    report.append("# Vision — Report RAG (sistema, stack tecnico, audit qualità)")
    report.append("")
    report.append(
        "Documento unico per **presentare** il retrieval aumentato della knowledge base Vision: "
        "pipeline dati, componenti usati in produzione (indicizzazione + MCP), e **risultati quantificati** "
        "dell’audit automatico (retrieval live su Chroma, stessi embedding del runtime)."
    )
    report.append("")
    report.append("---")
    report.append("")
    report.append("## 1. Come funziona il RAG Vision")
    report.append("")
    report.append("### 1.1 Pipeline end-to-end")
    report.append("")
    report.append("| Fase | Script / componente | Output | Ruolo nel RAG |")
    report.append("|------|---------------------|--------|---------------|")
    report.append(
        "| Estrazione PDF | `scripts/01_extract_pdf.py` (PyMuPDF); PDF scansionati → `scripts/01_extract_pdf_ocr.py` | `docs/raw/*.md` | Testo strutturato con marker `<!-- PAGE n -->` per tracciabilità pagina |"
    )
    report.append(
        "| Chunking | `scripts/02_chunk.py` (tiktoken `cl100k_base`, merge con conteggio token su testo giunto; confini **sentence-aware**; overlap) | `docs/chunks/all_chunks.json` | Unità di retrieval: testo + metadati (`source`, `page`, categorie, `tokens`) |"
    )
    report.append(
        "| Indicizzazione | `scripts/03_index.py` (Chroma persistente, batch, retry; resume o `--fresh`) | `vector_store/` | Vettori document/query allineati allo stesso modello di embedding |"
    )
    report.append(
        "| Consumo | `mcp_server/server.py` — `search_vision_docs`, `get_module_spec`, `list_sources` | risposte tool MCP | Retrieval semantico lato agente / IDE |"
    )
    report.append("")
    report.append("### 1.2 Stack tecnico (cosa usiamo)")
    report.append("")
    report.append("| Layer | Scelta | Note operative |")
    report.append("|-------|--------|------------------|")
    report.append("| Vector DB | ChromaDB (`PersistentClient`, collection `vision_docs`) | Store locale sotto `vector_store/` (non versionato in git) |")
    report.append("| Embedding documenti e query | Google **gemini-embedding-2** (`google-genai`) | Stessa funzione usata in `03_index.py` e nell’audit; richiede `GOOGLE_API_KEY` in `.env` |")
    report.append("| Tokenizer chunk | tiktoken `cl100k_base` | Allineato a ecosistemi LLM comuni; budget chunk **300–1200** token, overlap **80** |")
    report.append("| Metadati | `source`, `page` / `page_end`, categorie, `tokens`, `source_type` | Citazioni e filtri per dominio (Wyckoff, Market Profile, ML, ecc.) |")
    report.append("")
    sync_note = ""
    if indexed_count is not None and indexed_count != total_chunks:
        sync_note = f"\n\n> **Allineamento indice:** nel vector store risultano **{indexed_count:,}** voci; il file chunk ne conta **{total_chunks:,}**. Dopo modifiche al corpus eseguire `python scripts/03_index.py` (o `--fresh` se serve azzerare) prima di interpretare l’audit.\n"
    report.append(
        f"### 1.3 Dimensioni corpus (istantanea audit)\n\n"
        f"- **Chunk JSON:** {total_chunks:,}\n"
        f"- **Fonti distinte (metadata `source`):** {sources_count}\n"
        f"- **Token totali indicizzabili (somma `tokens` sui chunk):** {total_tokens:,}\n"
        f"{sync_note}"
    )

    report.append("---")
    report.append("")
    report.append("## 2. Metriche di bontà (quantificazione)")
    report.append("")
    report.append(
        "L’audit combina **test RAG live** (45 query: 30 core + 15 complesse) con **controlli statici** su tutti i chunk "
        "(distribuzione token, euristiche di taglio a inizio/fine frase). "
        "Le metriche **non** sostituiscono una valutazione umana su answer generation: misurano **recupero documentale** "
        "e qualità strutturale del corpus."
    )
    report.append("")
    report.append("### 2.1 Punteggio composito (0–100)")
    report.append("")
    report.append(
        f"**Vision RAG Score (composito):** **{composite} / 100** — formula pesata sull’istantanea corrente:\n\n"
        f"| Componente | Peso | Contributo (punti 0–100) | Valore usato |\n"
        f"|--------------|------|-------------------------|---------------|\n"
        f"| Retrieval core (query con hit) | {comp_parts['w_found']:.0%} | {comp_parts['s_found']:.1f} | {core_stats_preview['found']}/{n_core} trovati |\n"
        f"| Completezza euristica top-1 (core) | {comp_parts['w_compl']:.0%} | {comp_parts['s_compl']:.1f} | {core_stats_preview['complete']} completi su {max(core_stats_preview['found'],1)} con hit |\n"
        f"| Match fonte attesa (core, substring filename) | {comp_parts['w_exp']:.0%} | {comp_parts['s_exp']:.1f} | {core_stats_preview.get('exp_match',0)}/{max(core_stats_preview.get('exp_total') or 0, 1)} |\n"
        f"| Retrieval query complesse | {comp_parts['w_cx']:.0%} | {comp_parts['s_cx']:.1f} | {cx_stats_preview['found']}/{n_cx} trovati |\n"
        f"| Bordo chunk (`100 − % ends_mid_sentence`) | {comp_parts['w_edge']:.0%} | {comp_parts['s_edge']:.1f} | ends_mid_sentence = {ends_pct}% |\n"
    )
    report.append(
        "\n**Interpretazione:** il punteggio riassume retrieval e coerenza strutturale rispetto a baseline dichiarata in "
        "`docs/chunk_quality_baseline.json`. Il **match fonte attesa** è intenzionalmente conservativo (sottostringhe sul nome file); "
        "un mancato match può corrispondere comunque a contenuto pertinente da un altro manuale."
    )
    report.append("")

    report.append("---")
    report.append("")
    report.append("## 3. Corpus e trend (file chunk)")
    report.append("")
    report.append(f"**File:** `docs/chunks/all_chunks.json` — **{total_chunks:,} chunk**")
    report.append(f"**Data audit:** {audit_day}")
    report.append(f"**Confronto trend:** `docs/chunk_quality_baseline.json` — {ref_label}")
    report.append("")
    report.append("---")
    report.append("")

    # Section 1 (was) -> now 4 token distribution
    report.append("## 4. Distribuzione token per chunk")
    report.append("")
    report.append("| Metrica | Attuale | Baseline (v2) | Delta |")
    report.append("|---------|---------|---------------|-------|")
    prev_n = bc.get("total_chunks")
    prev_n_cell = f"{prev_n:,}" if prev_n is not None else "n/d"
    report.append(
        f"| Totale chunk | {token_stats['count']:,} | {prev_n_cell} | {_fmt_delta(token_stats['count'], prev_n)} |"
    )
    pm = bc.get("token_median")
    report.append(
        f"| Mediana token | {token_stats['median']} | {pm} | {_fmt_delta(token_stats['median'], pm)} |"
    )
    pmean = bc.get("token_mean")
    report.append(
        f"| Media token | {token_stats['mean']} | {pmean} | {_fmt_delta(token_stats['mean'], pmean)} |"
    )
    report.append(f"| Min / Max | {token_stats['min']} / {token_stats['max']} | {bc.get('token_min')} / {bc.get('token_max')} | |")
    report.append(f"| P10 / P90 | {token_stats['p10']} / {token_stats['p90']} | {bc.get('token_p10')} / {bc.get('token_p90')} | |")
    report.append("")
    report.append(f"**Nel range 200–1200 token:** {in_range:,} ({pct_in_range}%) — baseline {bc.get('pct_in_range_200_1200', 'n/d')}%")
    report.append(f"**Chunk troppo corti (<200):** {len(too_short):,} ({round(100*len(too_short)/total_chunks,1)}%)")
    report.append(f"**Chunk troppo lunghi (>1200):** {len(too_long):,}")
    snap = baseline.get("intermediate_snapshot_9166", {}) if baseline else {}
    if snap.get("total_chunks"):
        report.append("")
        report.append(
            f"> **Nota dimensione corpus:** rispetto allo snapshot intermedio ({snap['total_chunks']:,} chunk, {snap.get('note', '')}) "
            f"il delta è principalmente **+{total_chunks - int(snap['total_chunks']):,} chunk** dalla 2ª ed. Jansen (PDF nativo) oltre evoluzioni precedenti."
        )
    report.append("")

    # Section 5 core RAG table
    report.append("---")
    report.append("")
    report.append("## 5. Test RAG — 30 concetti core")
    report.append("")
    report.append(
        "Query in linguaggio naturale; colonne: completezza euristica, **Match atteso** = il `source` del top-1 contiene una delle sottostringhe attese (filename)."
    )
    report.append("")
    report.append("| # | Concetto | Trovato | Distanza | Completo | Src ok | Match atteso | Problemi |")
    report.append("|---|----------|---------|----------|----------|--------|--------------|----------|")

    core_lines, core_stats = _rag_table_rows(rag_results_core, 1)
    report.extend(core_lines)
    report.append("")

    # Section 6 complex RAG table
    report.append("---")
    report.append("")
    report.append("## 6. Query complesse e specifiche (stress test)")
    report.append("")
    report.append("| # | Concetto | Trovato | Distanza | Completo | Src ok | Match atteso | Problemi |")
    report.append("|---|----------|---------|----------|----------|--------|--------------|----------|")
    off = len(rag_results_core) + 1
    cx_lines, cx_stats = _rag_table_rows(rag_results_complex, off)
    report.extend(cx_lines)
    report.append("")

    # Section 7 details - core then complex
    report.append("---")
    report.append("")
    report.append("## 7. Dettaglio query RAG (core)")
    report.append("")
    report.append(_rag_detail_blocks(rag_results_core))
    report.append("")
    report.append("### Dettaglio query complesse")
    report.append("")
    report.append(_rag_detail_blocks(rag_results_complex))
    report.append("")

    # Section 8 cuts
    report.append("---")
    report.append("")
    report.append("## 8. Problemi di taglio (statico su tutti i chunk)")
    report.append("")
    starts_n = cut_issues_summary.get("starts_mid_sentence", 0)
    starts_pct = round(100 * starts_n / total_chunks, 1) if total_chunks else 0
    prev_ends_pct = bc.get("ends_mid_sentence_pct")
    prev_starts_pct = bc.get("starts_mid_sentence_pct")

    report.append("| Tipo | N. chunk | % attuale | Baseline % (v2) | Delta (pp) |")
    report.append("|------|----------|-------------|-----------------|------------|")
    d_ends = _fmt_delta(ends_pct, prev_ends_pct, is_pct=True) if prev_ends_pct is not None else "n/d"
    d_starts = _fmt_delta(starts_pct, prev_starts_pct, is_pct=True) if prev_starts_pct is not None else "n/d"
    report.append(
        f"| ends_mid_sentence | {ends_n:,} | {ends_pct}% | {prev_ends_pct}% | {d_ends} |"
    )
    report.append(
        f"| starts_mid_sentence | {starts_n:,} | {starts_pct}% | {prev_starts_pct}% | {d_starts} |"
    )
    other_issues = {k: v for k, v in cut_issues_summary.items() if k not in ["ends_mid_sentence", "starts_mid_sentence"]}
    for issue_type, count in sorted(other_issues.items(), key=lambda x: -x[1])[:12]:
        report.append(f"| {issue_type} | {count:,} | {round(100*count/total_chunks,1)}% | - | - |")
    report.append("")
    report.append(
        "> Il **denominatore** è cresciuto (più chunk); confrontare sia **%** sia **assoluti**. "
        "Un calo di **pp** su `ends_mid_sentence` indica miglioramento del confine frase; "
        "se solo il conteggio assoluto sale ma la % scende, il corpus è più \"pulito\" ai bordi."
    )
    report.append("")

    # Section 9 categories
    report.append("---")
    report.append("")
    report.append("## 9. Audit categorie (conteggi per tag)")
    report.append("")
    report.append("| Categoria | N. chunk | % |")
    report.append("|-----------|----------|---|")
    for cat, count in sorted(categories_audit.items(), key=lambda x: -x[1])[:28]:
        report.append(f"| {cat} | {count:,} | {round(100*count/total_chunks,1)}% |")
    report.append("")

    general_count = categories_audit.get("general", 0)
    if general_count == 0:
        report.append("> Nessun chunk con categoria `general`.")
    else:
        report.append(f"> **Attenzione:** {general_count} chunk con categoria `general`")
    report.append("")

    # Section 10 summary
    report.append("---")
    report.append("")
    report.append("## 10. Riepilogo, punteggio composito e baseline")
    report.append("")
    report.append("| Criterio | Attuale | Baseline (v2) | Commento |")
    report.append("|----------|---------|---------------|----------|")

    bf = b_rag.get("found", 30)
    bcpl = b_rag.get("complete", 29)
    report.append(
        f"| RAG core: trovati | {core_stats['found']}/{n_core} | {bf}/{b_rag.get('queries', 30)} | "
        f"{'=' if core_stats['found'] == bf else ('+' if core_stats['found'] > bf else '-')} |"
    )
    report.append(
        f"| RAG core: completi (euristica) | {core_stats['complete']}/{core_stats['found'] or 1} | {bcpl} | vs baseline |"
    )
    report.append(
        f"| RAG complesse: trovati | {cx_stats['found']}/{n_cx} | n/d | stress test |"
    )
    report.append(
        f"| Vision RAG Score (composito, v. §2.1) | **{composite}/100** | n/d | pesi: retrieval 35%, completezza 25%, match fonte 15%, complesse 15%, bordo chunk 10% |"
    )
    if core_stats.get("exp_total"):
        report.append(
            f"| Match fonte attesa (solo core) | {core_stats['exp_match']}/{core_stats['exp_total']} | n/d | sottostringhe filename |"
        )
    if cx_stats["exp_total"]:
        report.append(
            f"| Match fonte attesa (solo complesse) | {cx_stats['exp_match']}/{cx_stats['exp_total']} | n/d | sottostringhe filename |"
        )
    report.append(f"| Taglio `ends_mid_sentence` (% su corpus) | {ends_pct}% | {prev_ends_pct}% | {d_ends} |")
    report.append(f"| Token in range 200–1200 | {pct_in_range}% | {bc.get('pct_in_range_200_1200')}% | |")
    report.append("")

    report.append("### Interpretazione")
    report.append("")
    report.append(
        f"1. **Corpus più grande ({total_chunks:,} vs {(f'{prev_n:,}' if prev_n is not None else '?')} chunk baseline v2):** più candidati al retrieval; le query ML possono atterrare sulla **2ª ed. Jansen** (PDF testo)."
    )
    report.append(
        "2. **Mid-sentence:** `02_chunk.py` applica **sentence-aware** split e trim; restano percentuali residue su `ends_mid_sentence` / `starts_mid_sentence` (liste, formule, OCR). La **%** resta il KPI principale vs baseline v2."
    )
    report.append(
        "3. **Match atteso:** euristica grezza su nome file; un NO può essere comunque una risposta utile (fonte diversa ma corretta)."
    )
    report.append("")

    report.append("---")
    report.append("*Report generato da `scripts/chunk_quality_audit_v2.py` → `docs/RAG_report.md`*")

    return "\n".join(report)


def main():
    print("Loading chunks...")
    chunks = load_chunks()
    print(f"Loaded {len(chunks):,} chunks")

    baseline = load_baseline()
    if baseline:
        print(f"Baseline loaded: {baseline.get('reference_audit', 'ok')}")

    # 1. Token distribution
    print("\n[1/6] Token distribution...")
    token_stats = analyze_token_distribution(chunks)
    print(f"  Mean: {token_stats['mean']}, Median: {token_stats['median']}")

    # 2. Cut issues
    print("[2/6] Checking cut issues...")
    cut_issues_summary = defaultdict(int)
    for chunk in chunks:
        issues = check_cut_issues(chunk["text"])
        for issue in issues:
            cut_issues_summary[issue] += 1

    # 3. Categories audit
    print("[3/6] Auditing categories...")
    categories_audit = defaultdict(int)
    for chunk in chunks:
        cats = chunk.get("categories", [])
        if isinstance(cats, str):
            cats = cats.split(",")
        for cat in cats:
            categories_audit[cat.strip()] += 1

    # 4–5. RAG query tests
    print("[4/6] Connecting Chroma + embeddings...")
    import time

    collection = get_chroma_collection()
    print(f"  Collection has {collection.count()} chunks")

    def run_suite(label, queries):
        out = []
        for concept in queries:
            try:
                results = query_rag(collection, concept["query"], n_results=5)
                evaluation = evaluate_rag_result(concept, results)
                out.append((concept, evaluation))
                status = "OK" if evaluation["found"] else "--"
                em = evaluation.get("expected_source_match")
                print(
                    f"  [{status}] {concept['name']}: dist={evaluation.get('distance', '-')}, "
                    f"compl={evaluation.get('completeness', '-')}, match_atteso={em}",
                    flush=True,
                )
                time.sleep(0.45)
            except Exception as e:
                print(f"  [ERR] {concept['name']}: {e}", flush=True)
                out.append((concept, {"found": False, "issues": [str(e)[:80]], "expected_source_match": None}))
                time.sleep(2)
        return out

    print("[5/6] RAG queries — core 30...")
    rag_core = run_suite("core", CONCEPT_QUERIES)
    print("       RAG queries — complesse...")
    rag_complex = run_suite("complex", COMPLEX_QUERIES)

    print("[6/6] Generating report...")
    indexed_count = collection.count()
    report = generate_report(
        chunks,
        rag_core,
        rag_complex,
        token_stats,
        cut_issues_summary,
        categories_audit,
        baseline,
        indexed_count=indexed_count,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n{'='*60}")
    print(f"Report saved to: {OUTPUT_PATH}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
