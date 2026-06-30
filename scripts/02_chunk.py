"""
Step 2: Chunk extracted Markdown files into semantically coherent pieces.
Reads .md files from docs/raw/ and writes chunked JSON to docs/chunks/

Sentence-aware boundaries: oversized sections are split on sentence breaks where
possible; chunk ends are trimmed to the last full sentence when token budget allows.
Merge uses accurate `count_tokens` on joined text (not summed estimates).
"""

import json
import re
import sys
from pathlib import Path

import tiktoken

RAW_DIR = Path(r"C:\Users\Gabri\Vision\docs\raw")
CHUNKS_DIR = Path(r"C:\Users\Gabri\Vision\docs\chunks")

MIN_CHUNK_TOKENS = 300
MAX_CHUNK_TOKENS = 1200
OVERLAP_TOKENS = 80

# Drop first N merged chunks for specific stems (OCR cover + garbled TOC not indexed).
# Keys are md_path.stem without .md
DROP_LEADING_CHUNK_COUNT = {
    "Martin_Pring_on_Market_Momentum_-_PDF_Room": 3,
}

TOKENIZER = tiktoken.get_encoding("cl100k_base")

# Sentence boundary: split / trim after these (similar to chunk_quality_audit heuristic).
_SENT_SPLIT = re.compile(r"(?<=[.!?\u2026])(?=\s)")
_SENT_END_OK = re.compile(r"[.!?\u2026][\"')\]]*\s*$")

# Known books mapped to source_type and domain tags
# Keys are substrings matched against lowercased filename — more specific keys MUST come first
BOOK_METADATA = {
    # Wyckoff / Market Structure
    "wyckoff": {"source_type": "theory", "categories": ["pattern", "strategy", "methodology"]},
    "coulling": {"source_type": "theory", "categories": ["volume", "price_action"]},
    "grimes": {"source_type": "theory", "categories": ["market_structure", "price_action"]},
    "elliott": {"source_type": "theory", "categories": ["pattern", "wave_theory"]},
    # Market Profile
    "dalton": {"source_type": "theory", "categories": ["market_profile", "volume"]},
    "profit_with": {"source_type": "theory", "categories": ["market_profile", "volume"]},
    # Technical Analysis
    "murphy": {"source_type": "theory", "categories": ["technical_analysis"]},
    "pring": {"source_type": "theory", "categories": ["momentum", "technical_analysis"]},
    "aronson": {"source_type": "theory", "categories": ["evidence_based", "technical_analysis"]},
    "trading-system": {"source_type": "theory", "categories": ["strategy", "systematic", "technical_analysis"]},
    "analisi_tecnica": {"source_type": "theory", "categories": ["technical_analysis"]},
    "guida": {"source_type": "theory", "categories": ["technical_analysis", "strategy"]},
    # Quantitative / Algorithmic
    "prado": {"source_type": "theory", "categories": ["formula", "machine_learning", "quantitative"]},
    "_chan": {"source_type": "theory", "categories": ["algorithmic_trading", "quantitative"]},
    "machine_learning_for": {"source_type": "theory", "categories": ["machine_learning", "algorithmic_trading"]},
    "high-frequency": {"source_type": "theory", "categories": ["algorithmic_trading", "hft", "market_microstructure"]},
    "pedersen": {"source_type": "theory", "categories": ["quantitative", "portfolio", "risk"]},
    # Portfolio / Risk
    "active_portfolio": {"source_type": "theory", "categories": ["portfolio", "risk", "quantitative"]},
    "handbook_of_portfolio": {"source_type": "theory", "categories": ["portfolio", "risk", "formula"]},
    "portfolio": {"source_type": "theory", "categories": ["portfolio", "risk"]},
    # Volatility / Options
    "sinclair": {"source_type": "theory", "categories": ["volatility", "options"]},
    "options_volatility": {"source_type": "theory", "categories": ["volatility", "options", "formula"]},
    # Market Microstructure
    "microstructure": {"source_type": "theory", "categories": ["market_microstructure", "order_book"]},
    "limitorder": {"source_type": "theory", "categories": ["market_microstructure", "order_book", "hft"]},
    "price_impact": {"source_type": "theory", "categories": ["market_microstructure", "order_book", "formula"]},
    "flow_toxicity": {"source_type": "theory", "categories": ["market_microstructure", "hft", "flow_toxicity", "volume"]},
    "flash_boys": {"source_type": "theory", "categories": ["market_microstructure", "hft"]},
    # Machine Learning
    "reinforcement": {"source_type": "theory", "categories": ["machine_learning", "reinforcement_learning"]},
    "n-beats": {"source_type": "theory", "categories": ["machine_learning", "time_series"]},
    "temporal_fusion": {"source_type": "theory", "categories": ["machine_learning", "time_series"]},
    # Project specs
    "vision": {"source_type": "spec", "categories": ["architecture", "implementation"]},
}


def count_tokens(text: str) -> int:
    return len(TOKENIZER.encode(text))


def ends_at_sentence_terminal(text: str) -> bool:
    s = text.rstrip()
    if not s or s.endswith("---"):
        return True
    return bool(_SENT_END_OK.search(s))


def trim_suffix_to_last_sentence(text: str, min_tokens: int) -> str:
    """Remove trailing tail after last sentence-ending punctuation if we keep >= min_tokens."""
    t = text.rstrip()
    if not t or ends_at_sentence_terminal(t):
        return text
    last_end = 0
    for m in re.finditer(r"[.!?\u2026]+[\"'\")\]]*\s+", t):
        last_end = m.end()
    if last_end == 0:
        return text
    candidate = t[:last_end].rstrip()
    if count_tokens(candidate) >= min_tokens:
        return candidate
    return text


def split_sentences(text: str) -> list[str]:
    """Split on . ! ? … followed by whitespace (keeps delimiter on left segment)."""
    parts = _SENT_SPLIT.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def _word_split_with_trim(
    text: str,
    page: int,
    page_end: int,
    max_tokens: int,
    min_tokens: int,
    overlap_words: int,
) -> list[dict]:
    """Word-based split when sentence boundaries are sparse; trim end; overlap between parts."""
    result = []
    words = text.split()
    n = len(words)
    pos = 0
    while pos < n:
        start = pos
        current_words: list[str] = []
        while pos < n:
            w = words[pos]
            candidate = " ".join(current_words + [w])
            ct = count_tokens(candidate)
            if current_words and ct > max_tokens:
                break
            current_words.append(w)
            pos += 1
            if ct >= max_tokens:
                break
        if not current_words:
            current_words = [words[pos]]
            pos += 1
        chunk_text = " ".join(current_words)
        chunk_text = trim_suffix_to_last_sentence(chunk_text, min(min_tokens, 80))
        result.append(
            {
                "text": chunk_text,
                "page": page,
                "page_end": page_end,
                "tokens": count_tokens(chunk_text),
            }
        )
        adv = pos - start
        # Cap overlap so we advance by at least ~half a chunk; otherwise large word-overlap
        # vs small emitted windows creates floods of near-duplicate micro-chunks (bad for RAG).
        max_overlap = max(0, adv - max(1, adv // 2))
        ov = min(overlap_words, max_overlap)
        pos = start + adv - ov
        if pos <= start:
            pos = start + adv
    return result


def split_large_sections(sections: list[dict]) -> list[dict]:
    """Split sections that exceed MAX_CHUNK_TOKENS; prefer sentence boundaries."""
    result: list[dict] = []
    for section in sections:
        text = section["text"].strip()
        page = section["page"]
        pe = section.get("page_end", section["page"])
        real_tokens = count_tokens(text)

        if real_tokens <= MAX_CHUNK_TOKENS:
            refined = trim_suffix_to_last_sentence(text, MIN_CHUNK_TOKENS)
            result.append(
                {
                    "text": refined,
                    "page": page,
                    "page_end": pe,
                    "tokens": count_tokens(refined),
                }
            )
            continue

        sentences = split_sentences(text)
        if len(sentences) < 2:
            result.extend(
                _word_split_with_trim(
                    text, page, pe, MAX_CHUNK_TOKENS, MIN_CHUNK_TOKENS, overlap_words=24
                )
            )
            continue

        buf: list[str] = []
        buf_tokens = 0

        def flush_buf():
            nonlocal buf, buf_tokens
            if not buf:
                return
            joined = "\n\n".join(buf)
            joined = trim_suffix_to_last_sentence(joined, MIN_CHUNK_TOKENS)
            if not joined.strip():
                buf = []
                buf_tokens = 0
                return
            if count_tokens(joined) > MAX_CHUNK_TOKENS:
                result.extend(
                    _word_split_with_trim(
                        joined, page, pe, MAX_CHUNK_TOKENS, MIN_CHUNK_TOKENS, overlap_words=24
                    )
                )
            else:
                result.append(
                    {
                        "text": joined,
                        "page": page,
                        "page_end": pe,
                        "tokens": count_tokens(joined),
                    }
                )
            buf = []
            buf_tokens = 0

        i = 0
        while i < len(sentences):
            s = sentences[i]
            if not buf and count_tokens(s) > MAX_CHUNK_TOKENS:
                result.extend(
                    _word_split_with_trim(
                        s, page, pe, MAX_CHUNK_TOKENS, MIN_CHUNK_TOKENS, overlap_words=24
                    )
                )
                i += 1
                continue
            extra = count_tokens(s) + (2 if buf else 0)
            if buf and buf_tokens + extra > MAX_CHUNK_TOKENS:
                flush_buf()
            buf.append(s)
            buf_tokens = count_tokens("\n\n".join(buf))
            i += 1
        flush_buf()

    return result


def detect_book_meta(filename: str) -> dict:
    """Match filename to known book metadata."""
    fname_lower = filename.lower()
    for key, meta in BOOK_METADATA.items():
        if key in fname_lower:
            return meta
    return {"source_type": "theory", "categories": ["general"]}


def extract_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and return (metadata, body)."""
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    meta = {}
    body = text
    if match:
        for line in match.group(1).split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        body = text[match.end():]
    return meta, body


def split_into_sections(text: str) -> list[dict]:
    """Split text by page markers and attempted heading detection."""
    sections = []
    page_pattern = re.compile(r"<!-- PAGE (\d+) -->")

    parts = page_pattern.split(text)
    # parts alternates: [text_before, page_num, text_after, page_num, text_after, ...]

    current_page = 0
    for i, part in enumerate(parts):
        if i % 2 == 1:
            current_page = int(part)
            continue
        content = part.strip()
        if not content:
            continue

        paragraphs = re.split(r"\n{2,}", content)
        for para in paragraphs:
            para = para.strip()
            if not para or count_tokens(para) < 20:
                continue
            sections.append({
                "text": para,
                "page": current_page,
                "tokens": count_tokens(para),
            })

    return sections


def merge_small_sections(sections: list[dict]) -> list[dict]:
    """Merge sections that are too small, respecting max token limit."""
    if not sections:
        return []

    merged = [sections[0].copy()]

    for section in sections[1:]:
        last = merged[-1]
        combined_text = last["text"] + "\n\n" + section["text"]
        combined_tokens = count_tokens(combined_text)

        if last["tokens"] < MIN_CHUNK_TOKENS and combined_tokens <= MAX_CHUNK_TOKENS:
            last["text"] = combined_text
            last["tokens"] = combined_tokens
            if section["page"] > last.get("page_end", last["page"]):
                last["page_end"] = section["page"]
        else:
            merged.append(section.copy())

    return merged


def chunk_document(md_path: Path) -> list[dict]:
    """Full chunking pipeline for a single markdown file."""
    text = md_path.read_text(encoding="utf-8")
    frontmatter, body = extract_frontmatter(text)
    book_meta = detect_book_meta(md_path.stem)

    source_file = frontmatter.get("source_file", md_path.stem)

    sections = split_into_sections(body)
    sections = merge_small_sections(sections)
    sections = split_large_sections(sections)

    chunks = []
    for i, section in enumerate(sections):
        chunk = {
            "id": f"{md_path.stem}__chunk_{i:04d}",
            "text": section["text"],
            "tokens": section["tokens"],
            "source": source_file,
            "source_type": book_meta["source_type"],
            "categories": book_meta["categories"],
            "page": section["page"],
            "page_end": section.get("page_end", section["page"]),
            "chunk_index": i,
            "total_chunks": 0,
        }
        chunks.append(chunk)

    drop_n = DROP_LEADING_CHUNK_COUNT.get(md_path.stem, 0)
    if drop_n and len(chunks) > drop_n:
        chunks = chunks[drop_n:]
        stem = md_path.stem
        for i, chunk in enumerate(chunks):
            chunk["chunk_index"] = i
            chunk["id"] = f"{stem}__chunk_{i:04d}"

    for chunk in chunks:
        chunk["total_chunks"] = len(chunks)

    return chunks


def main():
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    md_files = sorted(RAW_DIR.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {RAW_DIR}")
        print("Run 01_extract_pdf.py first!")
        sys.exit(1)

    print(f"Found {len(md_files)} markdown files\n")

    all_chunks = []
    for i, md_path in enumerate(md_files, 1):
        print(f"[{i}/{len(md_files)}] Chunking: {md_path.name}...", end=" ", flush=True)
        try:
            chunks = chunk_document(md_path)
            all_chunks.extend(chunks)
            total_tokens = sum(c["tokens"] for c in chunks)
            print(f"OK ({len(chunks)} chunks, {total_tokens:,} tokens)")
        except Exception as e:
            print(f"ERROR: {e}")

    output_path = CHUNKS_DIR / "all_chunks.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Total tokens: {sum(c['tokens'] for c in all_chunks):,}")
    print(f"Avg tokens/chunk: {sum(c['tokens'] for c in all_chunks) // max(len(all_chunks), 1)}")
    print(f"Output: {output_path}")

    source_types = {}
    for c in all_chunks:
        st = c["source_type"]
        source_types[st] = source_types.get(st, 0) + 1
    print(f"\nBy source_type:")
    for st, count in sorted(source_types.items()):
        print(f"  {st}: {count} chunks")


if __name__ == "__main__":
    main()
