#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import fitz  # PyMuPDF

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output_pdf"
INPUT_PDF_DIR = SCRIPT_DIR / "put_your_pdf_here"


def collect_text_files(directory: Path) -> list[Path]:
    files = [p for p in directory.glob("*.txt") if p.is_file()]
    return sorted(files, key=sort_key)


def sort_key(path: Path) -> tuple[int, str]:
    match = re.search(r"(\d+)", path.stem)
    if match:
        return (int(match.group(1)), path.name)
    return (10**12, path.name)


def add_text_page(doc: fitz.Document, text: str) -> None:
    page = doc.new_page()
    margin = 36
    rect = page.rect + (margin, margin, -margin, -margin)
    page.insert_textbox(rect, text, fontsize=11)

def remove_empty_pages(doc: fitz.Document) -> None:
    empty_page_indexes = [
        i for i in range(doc.page_count) if doc.load_page(i).get_text("text").strip() == ""
    ]
    for index in reversed(empty_page_indexes):
        doc.delete_page(index)


def main() -> None:
    if not INPUT_PDF_DIR.exists():
        raise FileNotFoundError(f"Missing input directory: {INPUT_PDF_DIR}")

    pdf_files = sorted(p for p in INPUT_PDF_DIR.glob("*.pdf") if p.is_file())
    if not pdf_files:
        raise FileNotFoundError(f"No .pdf files found in: {INPUT_PDF_DIR}")
    if len(pdf_files) > 1:
        names = ", ".join(p.name for p in pdf_files)
        raise FileExistsError(f"Multiple PDFs found in {INPUT_PDF_DIR}: {names}")

    input_pdf_path = pdf_files[0]
    output_pdf_path = OUTPUT_DIR / f"{input_pdf_path.stem}_synthetic_test_data.pdf"

    if not OUTPUT_DIR.exists():
        raise FileNotFoundError(f"Missing output directory: {OUTPUT_DIR}")

    text_files = collect_text_files(OUTPUT_DIR)
    if not text_files:
        raise FileNotFoundError(f"No .txt files found in: {OUTPUT_DIR}")

    doc = fitz.open()
    for path in text_files:
        content = path.read_text(encoding="utf-8")
        add_text_page(doc, content)

    remove_empty_pages(doc)

    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_pdf_path.as_posix())
    doc.close()

    for path in text_files:
        path.unlink()


if __name__ == "__main__":
    main()
