"""
Step 1: Extract text from PDFs into clean Markdown files.
Reads all PDFs from the source folder and writes .md files to docs/raw/
"""

import sys
import os
from pathlib import Path

import pymupdf

SOURCE_DIR = Path(r"C:\Users\Gabri\Strategy&Indicators\MATERIALERAGVISION")
OUTPUT_DIR = Path(r"C:\Users\Gabri\Vision\docs\raw")


def sanitize_filename(name: str) -> str:
    safe = name.replace(".pdf", "").replace(".PDF", "")
    safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in safe)
    return safe.strip().replace("  ", " ").replace(" ", "_")


def extract_pdf(pdf_path: Path, output_dir: Path) -> dict:
    """Extract text from a single PDF and save as Markdown."""
    doc = pymupdf.open(str(pdf_path))
    safe_name = sanitize_filename(pdf_path.name)
    out_path = output_dir / f"{safe_name}.md"

    total_pages = doc.page_count
    total_chars = 0
    pages_with_text = 0

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"---\n")
        f.write(f"source_file: \"{pdf_path.name}\"\n")
        f.write(f"total_pages: {total_pages}\n")
        f.write(f"---\n\n")

        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text("text")
            if not text or not text.strip():
                continue

            pages_with_text += 1
            total_chars += len(text)

            f.write(f"\n\n<!-- PAGE {page_num + 1} -->\n\n")
            f.write(text.strip())
            f.write("\n")

    doc.close()

    return {
        "file": pdf_path.name,
        "output": out_path.name,
        "total_pages": total_pages,
        "pages_with_text": pages_with_text,
        "total_chars": total_chars,
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdfs_lower = sorted(SOURCE_DIR.glob("*.pdf"))
    pdfs_upper = [p for p in sorted(SOURCE_DIR.glob("*.PDF")) if p not in pdfs_lower]
    pdfs = pdfs_lower + pdfs_upper
    if not pdfs:
        print(f"No PDFs found in {SOURCE_DIR}")
        sys.exit(1)

    print(f"Found {len(pdfs)} PDFs in {SOURCE_DIR}\n")

    results = []
    for i, pdf_path in enumerate(pdfs, 1):
        print(f"[{i}/{len(pdfs)}] Extracting: {pdf_path.name}...", end=" ", flush=True)
        try:
            info = extract_pdf(pdf_path, OUTPUT_DIR)
            results.append(info)
            print(f"OK ({info['pages_with_text']} pages, {info['total_chars']:,} chars)")
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({"file": pdf_path.name, "error": str(e)})

    print(f"\n{'='*60}")
    print(f"Extraction complete: {len([r for r in results if 'error' not in r])}/{len(pdfs)} successful")
    total = sum(r.get("total_chars", 0) for r in results)
    print(f"Total extracted text: {total:,} characters")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
