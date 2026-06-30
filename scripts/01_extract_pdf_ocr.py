"""
OCR extraction for scanned PDFs (no selectable text).

Uses PyMuPDF + Tesseract (same stack as https://pymupdf.readthedocs.io/en/latest/recipes-ocr.html).

Prerequisites (Windows):
  winget install UB-Mannheim.TesseractOCR
  Or install Tesseract and ensure tessdata contains eng.traineddata.

Optional env:
  TESSDATA_PREFIX — path to the tessdata folder (the one containing eng.traineddata)
  Or pass --tessdata "C:\\Program Files\\Tesseract-OCR\\tessdata"

Default targets: the three scan-only books (0 native text in docs/raw).

Quality (toward “professional” use):
  - Default DPI raised to 200 (sharper than 150; use 250–300 for math-heavy scans, slower).
  - Optional two-column OCR (--dual-column / auto for Natenberg): renders left and right
    halves separately then concatenates — reduces column interleaving on textbook layouts.
  - For publication-grade formulas/tables, plan a second pass with layout-aware tools
    (e.g. Marker, Docling, or a vector PDF if you can source one).

Usage:
  python scripts/01_extract_pdf_ocr.py                    # defaults: dpi=200, dual-col auto
  python scripts/01_extract_pdf_ocr.py --dpi 250          # higher quality
  python scripts/01_extract_pdf_ocr.py --dual-column      # force two-column for ALL pdfs
  python scripts/01_extract_pdf_ocr.py --no-dual-column   # force full-page for all
  python scripts/01_extract_pdf_ocr.py --max-pages 5      # smoke test (overwrites .md!)
"""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import pymupdf as fitz

SOURCE_DIR = Path(r"C:\Users\Gabri\Strategy&Indicators\MATERIALERAGVISION")
OUTPUT_DIR = Path(r"C:\Users\Gabri\Vision\docs\raw")

# Exact PDF filenames in SOURCE_DIR (verified 2026-05-13)
DEFAULT_SCAN_PDFS = [
    "elliott-wave-principle-key-to-market-behavior-by-frost-and-prechter_compress.pdf",
    "Martin Pring on Market Momentum - PDF Room.pdf",
    "Options_Volatility_and_Pricing_Sheldon_N.pdf",
]

# Natenberg is strongly multi-column; split OCR reduces “Pur / Catt” style interleaving.
AUTO_DUAL_COLUMN = frozenset(
    {
        "Options_Volatility_and_Pricing_Sheldon_N.pdf",
    }
)


def sanitize_filename(name: str) -> str:
    safe = name.replace(".pdf", "").replace(".PDF", "")
    safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in safe)
    return safe.strip().replace("  ", " ").replace(" ", "_")


def discover_tessdata(cli_path: str | None) -> str:
    if cli_path:
        p = Path(cli_path)
        if (p / "eng.traineddata").exists():
            return str(p)
        raise SystemExit(f"--tessdata must be folder containing eng.traineddata: {cli_path}")

    env = os.environ.get("TESSDATA_PREFIX", "").strip().strip('"')
    if env:
        ep = Path(env)
        if (ep / "eng.traineddata").exists():
            return str(ep)

    candidates = [
        Path(r"C:\Program Files\Tesseract-OCR\tessdata"),
        Path(r"C:\Program Files (x86)\Tesseract-OCR\tessdata"),
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Tesseract-OCR" / "tessdata",
    ]
    for c in candidates:
        if (c / "eng.traineddata").exists():
            return str(c)

    raise SystemExit(
        "Tesseract tessdata not found. Install Tesseract (e.g. winget install UB-Mannheim.TesseractOCR) "
        "or set TESSDATA_PREFIX / pass --tessdata pointing to the tessdata folder."
    )


def ocr_page_full(page: fitz.Page, tessdata: str, dpi: int) -> str:
    """Single full-page OCR (PyMuPDF integrated path)."""
    tp = page.get_textpage_ocr(dpi=dpi, language="eng", full=True, tessdata=tessdata)
    return (page.get_text("text", textpage=tp) or "").strip()


def ocr_page_split_columns(page: fitz.Page, tessdata: str, dpi: int) -> str:
    """OCR left and right column regions separately; join for reading order (top-to-bottom per side)."""
    r = page.rect
    w, h = r.width, r.height
    if w < 120:  # degenerate
        return ocr_page_full(page, tessdata, dpi)

    mid = w * 0.5
    clips = (fitz.Rect(0, 0, mid, h), fitz.Rect(mid, 0, w, h))
    parts: list[str] = []
    for clip in clips:
        pix = page.get_pixmap(dpi=dpi, clip=clip)
        stream = pix.pdfocr_tobytes(compress=False, language="eng", tessdata=tessdata)
        ocr_doc = fitz.open(stream=stream)
        try:
            t = (ocr_doc[0].get_text("text") or "").strip()
        finally:
            ocr_doc.close()
        if t:
            parts.append(t)
    return "\n\n".join(parts)


def ocr_page_text(
    page: fitz.Page,
    tessdata: str,
    dpi: int,
    *,
    dual_column: bool,
) -> str:
    if dual_column:
        return ocr_page_split_columns(page, tessdata, dpi)
    return ocr_page_full(page, tessdata, dpi)


def extract_pdf_ocr(
    pdf_path: Path,
    output_dir: Path,
    tessdata: str,
    dpi: int,
    max_pages: int | None,
    start_page: int,
    dual_column: bool,
) -> dict:
    """Extract text via OCR; output format matches 01_extract_pdf.py."""
    doc = fitz.open(str(pdf_path))
    safe_name = sanitize_filename(pdf_path.name)
    out_path = output_dir / f"{safe_name}.md"

    total_pages = doc.page_count
    end_page = total_pages if max_pages is None else min(total_pages, start_page + max_pages)
    pages_done = 0
    total_chars = 0

    t0 = time.perf_counter()
    layout = "dual-column" if dual_column else "full-page"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f'source_file: "{pdf_path.name}"\n')
        f.write(f"total_pages: {total_pages}\n")
        f.write("extraction: ocr_pymupdf_tesseract\n")
        f.write(f"ocr_dpi: {dpi}\n")
        f.write(f"ocr_layout: {layout}\n")
        f.write("---\n\n")

        for page_num in range(start_page, end_page):
            page = doc[page_num]
            text = ocr_page_text(page, tessdata, dpi, dual_column=dual_column)
            if text:
                pages_done += 1
                total_chars += len(text)
                f.write(f"\n\n<!-- PAGE {page_num + 1} -->\n\n")
                f.write(text)
                f.write("\n")

            if (page_num - start_page + 1) % 10 == 0 or page_num == end_page - 1:
                elapsed = time.perf_counter() - t0
                print(
                    f"  {pdf_path.name[:50]}... page {page_num + 1}/{end_page} "
                    f"({pages_done} with text, {total_chars:,} chars, {elapsed:.0f}s)",
                    flush=True,
                )

    doc.close()
    return {
        "file": pdf_path.name,
        "output": out_path.name,
        "total_pages": total_pages,
        "pages_ocr": end_page - start_page,
        "pages_with_text": pages_done,
        "total_chars": total_chars,
        "seconds": round(time.perf_counter() - t0, 1),
        "ocr_layout": layout,
    }


def main():
    parser = argparse.ArgumentParser(description="OCR scanned PDFs into docs/raw markdown")
    parser.add_argument("--dpi", type=int, default=200, help="Render DPI for OCR (default 200)")
    parser.add_argument("--max-pages", type=int, default=None, help="Max pages per PDF (default: all)")
    parser.add_argument("--start-page", type=int, default=0, help="0-based start page index")
    parser.add_argument("--tessdata", type=str, default=None, help="Path to tessdata folder")
    g = parser.add_mutually_exclusive_group()
    g.add_argument(
        "--dual-column",
        action="store_true",
        help="Force two-column split OCR for every PDF in this run",
    )
    g.add_argument(
        "--no-dual-column",
        action="store_true",
        help="Disable two-column mode (override auto for Natenberg)",
    )
    parser.add_argument(
        "pdfs",
        nargs="*",
        help="PDF basenames under SOURCE_DIR (default: three scan-only books)",
    )
    args = parser.parse_args()

    tessdata = discover_tessdata(args.tessdata)
    print(f"Using tessdata: {tessdata}\n")

    names = args.pdfs if args.pdfs else DEFAULT_SCAN_PDFS
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    for i, name in enumerate(names, 1):
        pdf_path = SOURCE_DIR / name
        if not pdf_path.is_file():
            alt = SOURCE_DIR / name.replace("_", " ")
            if alt.is_file():
                pdf_path = alt
            else:
                print(f"[{i}/{len(names)}] SKIP (not found): {name}", flush=True)
                continue

        if args.dual_column:
            use_dual = True
        elif args.no_dual_column:
            use_dual = False
        else:
            use_dual = pdf_path.name in AUTO_DUAL_COLUMN

        mode = "dual-column" if use_dual else "full-page"
        print(f"[{i}/{len(names)}] OCR: {pdf_path.name}  (layout={mode}, dpi={args.dpi})...", flush=True)
        try:
            info = extract_pdf_ocr(
                pdf_path,
                OUTPUT_DIR,
                tessdata=tessdata,
                dpi=args.dpi,
                max_pages=args.max_pages,
                start_page=args.start_page,
                dual_column=use_dual,
            )
            results.append(info)
            print(
                f"  -> OK {info['output']}: {info['pages_with_text']}/{info['pages_ocr']} pages, "
                f"{info['total_chars']:,} chars in {info['seconds']}s\n",
                flush=True,
            )
        except Exception as e:
            print(f"  -> ERROR: {e}\n", flush=True)
            results.append({"file": name, "error": str(e)})

    ok = [r for r in results if "error" not in r]
    print("=" * 60)
    print(f"Done: {len(ok)}/{len(names)} OK")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
