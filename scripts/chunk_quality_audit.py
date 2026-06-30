"""
Chunk Quality Audit Script
Analyzes all_chunks.json for completeness, coherence, and token distribution.
Searches for key trading/finance concepts and validates chunk integrity.
Outputs: docs/legacy_chunk_quality_audit_v1.md (deprecato; usare chunk_quality_audit_v2.py → RAG_report.md)
"""

import json
import re
import statistics
from pathlib import Path
from collections import defaultdict

CHUNKS_PATH = Path(r"C:\Users\Gabri\Vision\docs\chunks\all_chunks.json")
OUTPUT_PATH = Path(r"C:\Users\Gabri\Vision\docs\legacy_chunk_quality_audit_v1.md")

# 30 key concepts to audit — spanning all major domains
KEY_CONCEPTS = [
    # Wyckoff / Market Structure
    {"name": "Spring (Wyckoff)", "patterns": [r"\bspring\b"], "context": "wyckoff accumulation/distribution event"},
    {"name": "Upthrust (Wyckoff)", "patterns": [r"\bupthrust\b", r"\bUT\b"], "context": "wyckoff distribution event"},
    {"name": "Sign of Strength (SOS)", "patterns": [r"\bSOS\b", r"sign of strength"], "context": "wyckoff phase signal"},
    {"name": "Accumulation Schematic", "patterns": [r"accumulation.*schematic", r"phase\s*[A-E].*accumulation"], "context": "wyckoff full schematic"},
    {"name": "Composite Operator", "patterns": [r"composite\s*(man|operator)", r"smart\s*money"], "context": "wyckoff concept of institutional player"},
    # Volume Analysis
    {"name": "OBV (On Balance Volume)", "patterns": [r"\bOBV\b", r"on.balance.volume"], "context": "volume indicator"},
    {"name": "CVD (Cumulative Volume Delta)", "patterns": [r"\bCVD\b", r"cumulative\s*volume\s*delta"], "context": "order flow indicator"},
    {"name": "VWAP", "patterns": [r"\bVWAP\b", r"volume.weighted.average.price"], "context": "volume-weighted price benchmark"},
    {"name": "RVOL (Relative Volume)", "patterns": [r"\bRVOL\b", r"relative\s*volume"], "context": "volume comparison metric"},
    {"name": "Volume Profile", "patterns": [r"volume\s*profile", r"volume\s*at\s*price"], "context": "distribution of volume by price"},
    # Order Flow / Market Profile
    {"name": "Delta (Order Flow)", "patterns": [r"\bdelta\b.*(?:order|flow|volume|bid|ask)", r"(?:order|flow).*\bdelta\b"], "context": "bid-ask volume differential"},
    {"name": "Market Profile (TPO)", "patterns": [r"market\s*profile", r"\bTPO\b", r"time.price.opportunity"], "context": "Dalton's market profile"},
    {"name": "Value Area", "patterns": [r"value\s*area", r"\bVAH\b", r"\bVAL\b", r"\bPOC\b"], "context": "market profile key levels"},
    {"name": "Initial Balance", "patterns": [r"initial\s*balance", r"\bIB\b.*(?:range|high|low)"], "context": "market profile first-hour range"},
    # Technical Analysis
    {"name": "Elliott Wave", "patterns": [r"elliott\s*wave", r"impulse\s*wave", r"corrective\s*wave"], "context": "wave theory pattern counting"},
    {"name": "Fibonacci Retracement", "patterns": [r"fibonacci\s*retrace", r"0\.618", r"0\.382"], "context": "key retracement levels"},
    {"name": "RSI Divergence", "patterns": [r"RSI.*divergen", r"divergen.*RSI"], "context": "momentum divergence signal"},
    {"name": "Bollinger Bands", "patterns": [r"bollinger\s*band", r"standard\s*deviation.*band"], "context": "volatility envelope indicator"},
    # Quantitative / ML
    {"name": "Sharpe Ratio", "patterns": [r"sharpe\s*ratio", r"risk.adjusted\s*return"], "context": "risk-adjusted performance metric"},
    {"name": "Mean Reversion", "patterns": [r"mean\s*reversion", r"mean.revert"], "context": "quantitative trading strategy"},
    {"name": "Cointegration", "patterns": [r"cointegrat", r"engle.granger", r"johansen"], "context": "statistical relationship for pairs trading"},
    {"name": "Kelly Criterion", "patterns": [r"kelly\s*criterion", r"kelly\s*formula", r"optimal\s*f\b"], "context": "optimal position sizing"},
    # Microstructure
    {"name": "Limit Order Book", "patterns": [r"limit\s*order\s*book", r"\bLOB\b"], "context": "market microstructure core"},
    {"name": "Bid-Ask Spread", "patterns": [r"bid.ask\s*spread", r"spread.*liquidity"], "context": "microstructure cost metric"},
    {"name": "Price Impact", "patterns": [r"price\s*impact", r"market\s*impact.*order"], "context": "execution cost model"},
    # Volatility / Options
    {"name": "Implied Volatility", "patterns": [r"implied\s*volatility", r"\bIV\b.*(?:option|volatil)"], "context": "options pricing key input"},
    {"name": "Volatility Smile/Skew", "patterns": [r"volatility\s*(?:smile|skew|surface)"], "context": "options IV shape across strikes"},
    {"name": "Greeks (Delta/Gamma/Theta/Vega)", "patterns": [r"\b(?:delta|gamma|theta|vega)\b.*option", r"option.*greek"], "context": "options risk sensitivities"},
    # Advanced Quant
    {"name": "CUSUM Filter", "patterns": [r"\bCUSUM\b", r"cumulative\s*sum.*filter"], "context": "de Prado event-driven sampling"},
    {"name": "Triple Barrier Method", "patterns": [r"triple\s*barrier", r"three\s*barrier"], "context": "de Prado labeling method"},
]


def load_chunks():
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def search_concept(chunks, concept):
    """Search for a concept across all chunks. Return matching chunks sorted by relevance."""
    matches = []
    for chunk in chunks:
        text_lower = chunk["text"].lower()
        score = 0
        for pattern in concept["patterns"]:
            found = re.findall(pattern, text_lower, re.IGNORECASE)
            score += len(found)
        if score > 0:
            matches.append({"chunk": chunk, "score": score})
    matches.sort(key=lambda x: -x["score"])
    return matches


def check_cut_issues(chunk_text):
    """Detect if a chunk appears to cut a definition, formula, or table mid-way."""
    issues = []
    
    # Ends mid-sentence (no terminal punctuation at the end)
    stripped = chunk_text.rstrip()
    if stripped and stripped[-1] not in ".!?:;)]\"\u2019\u201d" and not stripped.endswith("---"):
        last_line = stripped.split("\n")[-1].strip()
        if len(last_line) > 20 and not last_line.startswith("|") and not last_line.startswith("#"):
            issues.append("ends_mid_sentence")
    
    # Starts mid-sentence (lowercase letter at start, not a list item)
    first_line = chunk_text.lstrip().split("\n")[0].strip()
    if first_line and first_line[0].islower() and not first_line.startswith("-") and not first_line.startswith("*"):
        issues.append("starts_mid_sentence")
    
    # Unbalanced parentheses (formula cut)
    open_parens = chunk_text.count("(") - chunk_text.count(")")
    if abs(open_parens) > 2:
        issues.append(f"unbalanced_parens({open_parens:+d})")
    
    # Unbalanced brackets (formula cut)
    open_brackets = chunk_text.count("[") - chunk_text.count("]")
    if abs(open_brackets) > 2:
        issues.append(f"unbalanced_brackets({open_brackets:+d})")
    
    # Table cut: starts or ends with a pipe line but not a complete table
    lines = chunk_text.strip().split("\n")
    if lines:
        if lines[0].strip().startswith("|") and not lines[0].strip().startswith("| "):
            if len([l for l in lines if l.strip().startswith("|")]) < 2:
                issues.append("table_fragment_start")
        if lines[-1].strip().startswith("|"):
            if len([l for l in lines if l.strip().startswith("|")]) < 2:
                issues.append("table_fragment_end")
    
    # Incomplete formula markers (LaTeX-like)
    dollar_count = chunk_text.count("$$")
    if dollar_count % 2 != 0:
        issues.append("incomplete_latex_block")
    
    return issues


def check_section_boundary(chunk):
    """Check if chunk respects logical section boundaries."""
    text = chunk["text"]
    issues = []
    
    # Check if chunk contains a heading but doesn't start with it
    heading_matches = list(re.finditer(r"^#{1,4}\s+.+", text, re.MULTILINE))
    if heading_matches:
        first_heading_pos = heading_matches[0].start()
        text_before_heading = text[:first_heading_pos].strip()
        if text_before_heading and len(text_before_heading) > 50:
            issues.append("heading_not_at_start")
    
    return issues


def analyze_token_distribution(chunks):
    """Compute token statistics."""
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


def find_outliers(chunks, min_threshold=200, max_threshold=1200):
    """Find chunks outside ideal token range."""
    too_short = [c for c in chunks if c["tokens"] < min_threshold]
    too_long = [c for c in chunks if c["tokens"] > max_threshold]
    return too_short, too_long


def generate_report(chunks, concept_results, token_stats, too_short, too_long, cut_issues_summary, boundary_issues_summary):
    """Generate the markdown report."""
    total_chunks = len(chunks)
    in_range = total_chunks - len(too_short) - len(too_long)
    pct_in_range = round(100 * in_range / total_chunks, 1)
    
    # Source distribution
    source_counts = defaultdict(int)
    for c in chunks:
        source_counts[c["source"]] += 1
    
    report = []
    report.append("# Chunk Quality Audit Report")
    report.append("")
    report.append(f"**Data:** `docs/chunks/all_chunks.json`")
    report.append(f"**Total chunk analizzati:** {total_chunks:,}")
    report.append(f"**Data audit:** 2026-05-13")
    report.append("")
    report.append("---")
    report.append("")
    
    # Section 1: Token Distribution
    report.append("## 1. Distribuzione Token per Chunk")
    report.append("")
    report.append("| Metrica | Valore |")
    report.append("|---------|--------|")
    report.append(f"| Totale chunk | {token_stats['count']:,} |")
    report.append(f"| Min tokens | {token_stats['min']} |")
    report.append(f"| Max tokens | {token_stats['max']} |")
    report.append(f"| Media | {token_stats['mean']} |")
    report.append(f"| Mediana | {token_stats['median']} |")
    report.append(f"| Deviazione std | {token_stats['stdev']} |")
    report.append(f"| Percentile 10° | {token_stats['p10']} |")
    report.append(f"| Percentile 25° | {token_stats['p25']} |")
    report.append(f"| Percentile 75° | {token_stats['p75']} |")
    report.append(f"| Percentile 90° | {token_stats['p90']} |")
    report.append("")
    report.append(f"**Chunk nel range ideale (200-1200 token):** {in_range:,} ({pct_in_range}%)")
    report.append(f"**Chunk troppo corti (<200):** {len(too_short):,} ({round(100*len(too_short)/total_chunks,1)}%)")
    report.append(f"**Chunk troppo lunghi (>1200):** {len(too_long):,} ({round(100*len(too_long)/total_chunks,1)}%)")
    report.append("")
    
    # Token histogram (text-based)
    report.append("### Distribuzione per fasce")
    report.append("")
    ranges = [(0, 100), (100, 200), (200, 400), (400, 600), (600, 800), (800, 1000), (1000, 1200), (1200, 1500), (1500, 2000), (2000, 99999)]
    range_labels = ["0-99", "100-199", "200-399", "400-599", "600-799", "800-999", "1000-1199", "1200-1499", "1500-1999", "2000+"]
    report.append("| Range Token | Count | % | Stato |")
    report.append("|-------------|-------|---|-------|")
    for (lo, hi), label in zip(ranges, range_labels):
        count = sum(1 for c in chunks if lo <= c["tokens"] < hi)
        pct = round(100 * count / total_chunks, 1)
        if hi <= 200:
            stato = "⚠️ Troppo corto"
        elif hi <= 1200 or (lo >= 200 and hi <= 1200):
            stato = "✅ Ideale"
        elif lo >= 1200:
            stato = "⚠️ Troppo lungo"
        else:
            stato = "✅ Ideale"
        # fix logic
        if lo < 200:
            stato = "⚠️ Troppo corto"
        elif lo >= 1200:
            stato = "⚠️ Troppo lungo"
        else:
            stato = "✅ Ideale"
        report.append(f"| {label} | {count:,} | {pct}% | {stato} |")
    report.append("")
    
    # Section 2: Concept Search Results
    report.append("---")
    report.append("")
    report.append("## 2. Verifica Concetti Chiave (Quality Audit)")
    report.append("")
    report.append("Per ogni concetto, si valuta:")
    report.append("- **Trovato:** il concetto è presente nel RAG?")
    report.append("- **Chunk migliore completo:** il chunk top contiene una definizione/spiegazione completa?")
    report.append("- **Coerenza:** il chunk è tematicamente coerente (non mescola argomenti diversi)?")
    report.append("- **Problemi di taglio:** il chunk taglia definizioni, formule o tabelle?")
    report.append("")
    report.append("| # | Concetto | Trovato | N. Chunk | Chunk Top Completo | Coerente | Problemi |")
    report.append("|---|----------|---------|----------|-------------------|----------|----------|")
    
    for i, (concept, result) in enumerate(concept_results, 1):
        n_matches = result["n_matches"]
        found = "✅" if n_matches > 0 else "❌"
        
        if n_matches > 0:
            top_chunk = result["top_chunk"]
            completeness = result["completeness"]
            coherence = result["coherence"]
            problems = result["problems"]
            
            compl_icon = "✅" if completeness == "complete" else ("⚠️" if completeness == "partial" else "❌")
            coher_icon = "✅" if coherence == "coherent" else "⚠️"
            prob_text = ", ".join(problems) if problems else "Nessuno"
        else:
            compl_icon = "N/A"
            coher_icon = "N/A"
            prob_text = "Non trovato"
        
        report.append(f"| {i} | {concept['name']} | {found} | {n_matches} | {compl_icon} | {coher_icon} | {prob_text} |")
    
    report.append("")
    
    # Section 3: Detailed concept analysis
    report.append("---")
    report.append("")
    report.append("## 3. Analisi Dettagliata Concetti")
    report.append("")
    
    for concept, result in concept_results:
        if result["n_matches"] == 0:
            continue
        report.append(f"### {concept['name']}")
        report.append("")
        report.append(f"- **Match totali:** {result['n_matches']} chunk")
        report.append(f"- **Chunk migliore:** `{result['top_chunk']['id']}` (score: {result['top_score']}, {result['top_chunk']['tokens']} token)")
        report.append(f"- **Source:** {result['top_chunk']['source']} (pag. {result['top_chunk']['page']}-{result['top_chunk']['page_end']})")
        report.append(f"- **Completezza:** {result['completeness']}")
        report.append(f"- **Coerenza:** {result['coherence']}")
        if result["problems"]:
            report.append(f"- **Problemi:** {', '.join(result['problems'])}")
        report.append("")
        # Show first 300 chars of top chunk
        preview = result["top_chunk"]["text"][:400].replace("\n", " ").strip()
        report.append(f"> {preview}...")
        report.append("")
    
    # Section 4: Cut issues
    report.append("---")
    report.append("")
    report.append("## 4. Problemi di Taglio (Chunk Boundary Issues)")
    report.append("")
    report.append(f"**Chunk analizzati:** {total_chunks:,}")
    report.append("")
    report.append("| Tipo Problema | N. Chunk Affetti | % |")
    report.append("|---------------|-----------------|---|")
    for issue_type, count in sorted(cut_issues_summary.items(), key=lambda x: -x[1]):
        report.append(f"| {issue_type} | {count:,} | {round(100*count/total_chunks,1)}% |")
    report.append("")
    
    # Section 5: Boundary issues
    report.append("---")
    report.append("")
    report.append("## 5. Rispetto Confini Sezioni Logiche")
    report.append("")
    report.append(f"**Chunk con heading non all'inizio:** {boundary_issues_summary.get('heading_not_at_start', 0):,} ({round(100*boundary_issues_summary.get('heading_not_at_start',0)/total_chunks,1)}%)")
    report.append("")
    report.append("Questi chunk contengono un titolo di sezione (`#`, `##`, etc.) ma iniziano con del testo precedente, ")
    report.append("suggerendo che il confine del chunk non rispetta la separazione logica tra sezioni.")
    report.append("")
    
    # Section 6: Outliers
    report.append("---")
    report.append("")
    report.append("## 6. Chunk Outlier")
    report.append("")
    
    report.append("### 6.1 Chunk troppo corti (<200 token)")
    report.append("")
    if too_short:
        report.append(f"**Totale:** {len(too_short)} chunk")
        report.append("")
        # Group by source
        short_by_source = defaultdict(list)
        for c in too_short:
            short_by_source[c["source"]].append(c)
        report.append("| Source | N. Chunk Corti | Token Range | Possibile Causa |")
        report.append("|--------|---------------|-------------|-----------------|")
        for source, src_chunks in sorted(short_by_source.items(), key=lambda x: -len(x[1])):
            tok_range = f"{min(c['tokens'] for c in src_chunks)}-{max(c['tokens'] for c in src_chunks)}"
            # Heuristic: determine likely cause
            causes = []
            for c in src_chunks[:3]:
                if c["chunk_index"] == 0 or c["chunk_index"] == c["total_chunks"] - 1:
                    causes.append("inizio/fine documento")
                elif re.search(r"^#{1,4}\s", c["text"]):
                    causes.append("heading isolato")
                elif c["text"].count("|") > 5:
                    causes.append("tabella frammentata")
                else:
                    causes.append("paragrafo breve")
            cause = ", ".join(set(causes[:2]))
            report.append(f"| {source[:50]} | {len(src_chunks)} | {tok_range} | {cause} |")
    else:
        report.append("Nessun chunk sotto i 200 token.")
    report.append("")
    
    report.append("### 6.2 Chunk troppo lunghi (>1200 token)")
    report.append("")
    if too_long:
        report.append(f"**Totale:** {len(too_long)} chunk")
        report.append("")
        long_by_source = defaultdict(list)
        for c in too_long:
            long_by_source[c["source"]].append(c)
        report.append("| Source | N. Chunk Lunghi | Token Range | Possibile Causa |")
        report.append("|--------|----------------|-------------|-----------------|")
        for source, src_chunks in sorted(long_by_source.items(), key=lambda x: -len(x[1])):
            tok_range = f"{min(c['tokens'] for c in src_chunks)}-{max(c['tokens'] for c in src_chunks)}"
            causes = []
            for c in src_chunks[:3]:
                if c["text"].count("|") > 10:
                    causes.append("tabella lunga")
                elif re.search(r"\$\$|\\\[|\\frac|\\sum", c["text"]):
                    causes.append("blocco formule")
                elif c["text"].count("\n") > 30:
                    causes.append("sezione densa")
                else:
                    causes.append("contenuto denso")
            cause = ", ".join(set(causes[:2]))
            report.append(f"| {source[:50]} | {len(src_chunks)} | {tok_range} | {cause} |")
    else:
        report.append("Nessun chunk sopra i 1200 token.")
    report.append("")
    
    # Section 7: Source Distribution
    report.append("---")
    report.append("")
    report.append("## 7. Distribuzione Chunk per Source")
    report.append("")
    report.append("| Source | N. Chunk | % |")
    report.append("|--------|----------|---|")
    for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        report.append(f"| {source[:60]} | {count} | {round(100*count/total_chunks,1)}% |")
    report.append("")
    
    # Section 8: Summary and Recommendations
    report.append("---")
    report.append("")
    report.append("## 8. Riepilogo e Raccomandazioni")
    report.append("")
    
    # Calculate overall scores
    concepts_found = sum(1 for _, r in concept_results if r["n_matches"] > 0)
    concepts_complete = sum(1 for _, r in concept_results if r.get("completeness") == "complete")
    concepts_partial = sum(1 for _, r in concept_results if r.get("completeness") == "partial")
    
    report.append("### Punteggio Complessivo")
    report.append("")
    report.append(f"| Criterio | Risultato | Giudizio |")
    report.append(f"|----------|-----------|----------|")
    report.append(f"| Concetti trovati | {concepts_found}/{len(concept_results)} | {'✅' if concepts_found >= 25 else '⚠️'} |")
    report.append(f"| Concetti completi | {concepts_complete}/{concepts_found} | {'✅' if concepts_complete >= 20 else '⚠️'} |")
    report.append(f"| Chunk in range ideale | {pct_in_range}% | {'✅' if pct_in_range >= 80 else '⚠️'} |")
    
    cut_total = sum(cut_issues_summary.values())
    cut_pct = round(100 * cut_total / total_chunks, 1) if total_chunks > 0 else 0
    report.append(f"| Chunk senza problemi taglio | {round(100-cut_pct,1)}% | {'✅' if cut_pct < 20 else '⚠️'} |")
    
    boundary_total = sum(boundary_issues_summary.values())
    boundary_pct = round(100 * boundary_total / total_chunks, 1) if total_chunks > 0 else 0
    report.append(f"| Confini sezione rispettati | {round(100-boundary_pct,1)}% | {'✅' if boundary_pct < 15 else '⚠️'} |")
    report.append("")
    
    report.append("### Raccomandazioni")
    report.append("")
    if len(too_short) > total_chunks * 0.05:
        report.append(f"1. **Chunk corti:** {len(too_short)} chunk sotto 200 token — valutare merge più aggressivo o soglia MIN più alta")
    if len(too_long) > 0:
        report.append(f"2. **Chunk lunghi:** {len(too_long)} chunk sopra 1200 token — il splitting non funziona per tutti i casi (tabelle, formule)")
    if cut_pct > 15:
        report.append(f"3. **Problemi di taglio:** {cut_pct}% dei chunk ha almeno un problema — considerare splitting semantico")
    if concepts_found < len(concept_results):
        missing = [c["name"] for c, r in concept_results if r["n_matches"] == 0]
        report.append(f"4. **Concetti mancanti:** {', '.join(missing)} — verificare se presenti nei raw e se il chunking li perde")
    if boundary_pct > 10:
        report.append(f"5. **Confini sezione:** {boundary_pct}% chunk non rispetta heading — considerare split su heading")
    
    report.append("")
    report.append("---")
    report.append("*Report generato automaticamente da `scripts/chunk_quality_audit.py`*")
    
    return "\n".join(report)


def evaluate_concept_chunk(concept, top_match):
    """Evaluate completeness and coherence of the top matching chunk for a concept."""
    chunk = top_match["chunk"]
    text = chunk["text"]
    text_lower = text.lower()
    
    # Completeness: does the chunk contain a full definition/explanation?
    completeness_signals = {
        "has_definition": bool(re.search(r"(?:is |are |refers to |defined as |measures |represents |indicates )", text_lower)),
        "has_formula": bool(re.search(r"[=×÷\+\-\*/].*[a-zA-Z]|\\frac|\$\$", text)),
        "has_explanation": len(text) > 200,
        "has_context": bool(re.search(r"(?:used |when |example|for instance|trading|market)", text_lower)),
    }
    
    positive_signals = sum(completeness_signals.values())
    if positive_signals >= 3:
        completeness = "complete"
    elif positive_signals >= 2:
        completeness = "partial"
    else:
        completeness = "incomplete"
    
    # Coherence: is the chunk thematically focused?
    # Simple heuristic: count distinct topic switches
    lines = text.split("\n")
    non_empty_lines = [l for l in lines if l.strip()]
    
    coherence = "coherent"
    # If chunk contains content from multiple very different topics, flag it
    heading_count = sum(1 for l in non_empty_lines if re.match(r"^#{1,4}\s", l))
    if heading_count > 3:
        coherence = "mixed_topics"
    
    # Check for cut issues specific to this chunk
    problems = check_cut_issues(text)
    section_issues = check_section_boundary(chunk)
    problems.extend(section_issues)
    
    return completeness, coherence, problems


def main():
    print("Loading chunks...")
    chunks = load_chunks()
    print(f"Loaded {len(chunks):,} chunks")
    
    # 1. Token distribution analysis
    print("\n[1/6] Analyzing token distribution...")
    token_stats = analyze_token_distribution(chunks)
    print(f"  Min: {token_stats['min']}, Max: {token_stats['max']}, Mean: {token_stats['mean']}, Median: {token_stats['median']}")
    
    # 2. Find outliers
    print("[2/6] Finding outliers...")
    too_short, too_long = find_outliers(chunks)
    print(f"  Too short (<200): {len(too_short)}")
    print(f"  Too long (>1200): {len(too_long)}")
    
    # 3. Concept search
    print("[3/6] Searching key concepts...")
    concept_results = []
    for concept in KEY_CONCEPTS:
        matches = search_concept(chunks, concept)
        if matches:
            top = matches[0]
            completeness, coherence, problems = evaluate_concept_chunk(concept, top)
            result = {
                "n_matches": len(matches),
                "top_chunk": top["chunk"],
                "top_score": top["score"],
                "completeness": completeness,
                "coherence": coherence,
                "problems": problems,
            }
        else:
            result = {"n_matches": 0}
        concept_results.append((concept, result))
        status = "[OK]" if result["n_matches"] > 0 else "[--]"
        print(f"  {status} {concept['name']}: {result['n_matches']} matches")
    
    # 4. Check cut issues across all chunks
    print("[4/6] Checking cut issues across all chunks...")
    cut_issues_summary = defaultdict(int)
    for chunk in chunks:
        issues = check_cut_issues(chunk["text"])
        for issue in issues:
            cut_issues_summary[issue] += 1
    
    # 5. Check section boundaries
    print("[5/6] Checking section boundaries...")
    boundary_issues_summary = defaultdict(int)
    for chunk in chunks:
        issues = check_section_boundary(chunk)
        for issue in issues:
            boundary_issues_summary[issue] += 1
    
    # 6. Generate report
    print("[6/6] Generating report...")
    report = generate_report(chunks, concept_results, token_stats, too_short, too_long, cut_issues_summary, boundary_issues_summary)
    
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n{'='*60}")
    print(f"Report saved to: {OUTPUT_PATH}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
