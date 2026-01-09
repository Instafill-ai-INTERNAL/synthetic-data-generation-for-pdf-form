#!/usr/bin/env python3
from __future__ import annotations

import base64
from pathlib import Path

import fitz  # PyMuPDF
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_PDF_DIR = SCRIPT_DIR / "put_your_pdf_here"
OUTPUT_DIR = SCRIPT_DIR / "output_pdf"
SCREENSHOT_DIR = SCRIPT_DIR / "screenshots"
MODEL = "gpt-5.2"
TEMPERATURE = 0.2


def page_has_widgets(page: fitz.Page) -> bool:
    widgets = page.widgets()
    return bool(widgets)


def render_page_png(page: fitz.Page, path: Path, dpi: int = 150) -> None:
    pix = page.get_pixmap(dpi=dpi)
    path.parent.mkdir(parents=True, exist_ok=True)
    pix.save(path.as_posix())


def encode_image_base64(path: Path) -> str:
    data = path.read_bytes()
    return base64.b64encode(data).decode("ascii")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    if not INPUT_PDF_DIR.exists():
        raise FileNotFoundError(f"Missing input directory: {INPUT_PDF_DIR}")

    pdf_files = sorted(p for p in INPUT_PDF_DIR.glob("*.pdf") if p.is_file())
    if not pdf_files:
        raise FileNotFoundError(f"No .pdf files found in: {INPUT_PDF_DIR}")

    client = OpenAI()

    for input_pdf_path in pdf_files:
        print(f"Processing: {input_pdf_path.name}")
        pdf_stem = input_pdf_path.stem
        pdf_output_dir = OUTPUT_DIR / pdf_stem
        pdf_screenshot_dir = SCREENSHOT_DIR / pdf_stem

        ensure_dir(pdf_output_dir)
        ensure_dir(pdf_screenshot_dir)

        doc = fitz.open(input_pdf_path.as_posix())

        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            page_number = page_index + 1

            txt_path = pdf_output_dir / f"page_{page_number:03d}.txt"
            if txt_path.exists():
                continue

            if not page_has_widgets(page):
                txt_path.write_text("", encoding="utf-8")
                continue

            screenshot_path = pdf_screenshot_dir / f"page_{page_number:03d}.png"
            render_page_png(page, screenshot_path)

            image_b64 = encode_image_base64(screenshot_path)

            prompt = (
                "You are given a screenshot of a PDF form page. "
                "Return ONLY plain text lines in the format `Field Name: Value` "
                "for each fillable field visible on this page. "
                "Generate fictional but realistic synthetic values. "
                "Do not include fields that are not visible on this page. "
                "Do not add any extra commentary or formatting."
            )

            response = client.responses.create(
                model=MODEL,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{image_b64}",
                            },
                        ],
                    }
                ],
            )

            output_text = response.output_text or ""
            txt_path.write_text(output_text, encoding="utf-8")
        
        doc.close()


if __name__ == "__main__":
    main()
