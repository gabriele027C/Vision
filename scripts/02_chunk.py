"""
Step 2: Chunk extracted Markdown files into semantically coherent pieces.
Reads .md files from docs/raw/ and writes chunked JSON to docs/chunks/
"""

import json
import re
import sys
from pathlib import Path

import tiktoken

RAW_DIR = Path(r"C:\Users\Gabri\Vision\docs\raw")
CHUNKS_DIR = Path(r"C:\Users\Gabri\Vision\docs\chunks")

MIN_CHUNK_TOKENS = 200
MAX_CHUNK_TOKENS = 1200
OVERLAP_TOKENS = 100

TOKENIZER = tiktoken.get_encoding("cl100k_base")

# Known books mapped to source_type and domain tags
BOOK_METADATA = {
    "wyckoff": {"source_type": "theory", "categories": ["pattern", "strategy", "methodology"]},
    "coulling": {"source_type": "theory", "categories": ["volume", "price_action"]},
    "prado": {"source_type": "theory", "categories": ["formula", "machine_learning", "quantitative"]},
    "elliott": {"source_type": "theory", "categories": ["pattern", "wave_theory"]},
    "dalton": {"source_type": "theory", "categories": ["market_profile", "volume"]},
    "murphy": {"source_type": "theory", "categories": ["technical_analysis"]},
    "pring": {"source_type": "theory", "categories": ["momentum", "technical_analysis"]},
    "chan": {"source_type": "theory", "categories": ["algorithmic_trading", "quantitative"]},
    "aronson": {"source_type": "theory", "categories": ["evidence_based", "technical_analysis"]},
    "sinclair": {"source_type": "theory", "categories": ["volatility", "options"]},
    "grimes": {"source_type": "theory", "categories": ["market_structure", "price_action"]},
    "microstructure": {"source_type": "theory", "categories": ["market_microstructure", "order_book"]},
    "limit_order": {"source_type": "theory", "categories": ["market_microstructure", "order_book"]},
    "flash_boys": {"source_type": "theory", "categories": ["market_microstructure", "hft"]},
    "reinforcement": {"source_type": "theory", "categories": ["machine_learning", "reinforcement_learning"]},
    "n-beats": {"source_type": "theory", "categories": ["machine_learning", "time_series"]},
    "temporal_fusion": {"source_type": "theory", "categories": ["machine_learning", "time_series"]},
    "portfolio": {"source_type": "theory", "categories": ["portfolio", "risk"]},
    "trading_systems": {"source_type": "theory", "categories": ["strategy", "systematic"]},
    "analisi_tecnica": {"source_type": "theory", "categories": ["technical_analysis"]},
    "guida": {"source_type": "theory", "categories": ["technical_analysis", "strategy"]},
    "vision": {"source_type": "spec", "categories": ["architecture", "implementation"]},
}


def count_tokens(text: str) -> int:
    return len(TOKENIZER.encode(text))


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
        combined_tokens = last["tokens"] + section["tokens"]

        if last["tokens"] < MIN_CHUNK_TOKENS and combined_tokens <= MAX_CHUNK_TOKENS:
            last["text"] = last["text"] + "\n\n" + section["text"]
            last["tokens"] = combined_tokens
            if section["page"] > last.get("page_end", last["page"]):
                last["page_end"] = section["page"]
        else:
            merged.append(section.copy())

    return merged


def split_large_sections(sections: list[dict]) -> list[dict]:
    """Split sections that exceed MAX_CHUNK_TOKENS."""
    result = []
    for section in sections:
        if section["tokens"] <= MAX_CHUNK_TOKENS:
            result.append(section)
            continue

        words = section["text"].split()
        current_words = []
        current_tokens = 0

        for word in words:
            word_tokens = count_tokens(word + " ")
            if current_tokens + word_tokens > MAX_CHUNK_TOKENS and current_words:
                text = " ".join(current_words)
                result.append({
                    "text": text,
                    "page": section["page"],
                    "tokens": count_tokens(text),
                })
                overlap_words = current_words[-20:]
                current_words = overlap_words + [word]
                current_tokens = count_tokens(" ".join(current_words))
            else:
                current_words.append(word)
                current_tokens += word_tokens

        if current_words:
            text = " ".join(current_words)
            result.append({
                "text": text,
                "page": section.get("page_end", section["page"]),
                "tokens": count_tokens(text),
            })

    return result


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
