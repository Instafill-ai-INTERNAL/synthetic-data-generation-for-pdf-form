# Synthetic PDF Form Data Generator

Generate synthetic key-value text for PDF form pages using the OpenAI Responses API, then merge the results into a PDF.

## Setup

1) Create a folder named `put_your_pdf_here` next to the scripts.
2) Place exactly one `.pdf` file inside `put_your_pdf_here`.
3) Install dependencies:

```bash
pip install pymupdf openai
```

4) Set your API key:

```bash
export OPENAI_API_KEY="your_key_here"
```

## Run

```bash
python generate_page_texts.py
```

This will:
- Inspect each PDF page for form widgets.
- For pages with widgets, render a screenshot and call the OpenAI API to generate synthetic values.
- For pages without widgets, create an empty text file.
- Merge all page text files into a PDF named `<original>_synthetic_test_data.pdf`.
- Remove empty pages from the merged PDF.

## Output

- Per-page text files: `output_pdf/page_###.txt`
- Page screenshots: `screenshots/page_###.png`
- Merged PDF: `output_pdf/<original>_synthetic_test_data.pdf`

## Notes

- If a page text file already exists, that page is skipped to minimize API calls.
- The script expects exactly one PDF in `put_your_pdf_here`.
- Update `MODEL` in `generate_page_texts.py` if you want a different model.
