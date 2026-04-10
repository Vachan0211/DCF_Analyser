import pdfplumber
import re
from pathlib import Path


FINANCIAL_KEYWORDS = [
    "consolidated statements of earnings",
    "consolidated statements of operations",
    "consolidated balance sheet",
    "consolidated statements of cash flows",
    "net sales",
    "net earnings",
    "total assets",
    "stockholders equity",
    "operating activities",
]


def extract_financial_pages(pdf_path: str) -> str:
    """
    Opens a 10-K PDF, identifies pages containing financial statements,
    and returns their combined text. Limits to 40 pages max to stay
    within Claude API context limits.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    print(f"Opening: {pdf_path.name}")

    financial_pages = []
    all_pages_text = []

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages in PDF: {total_pages}")

        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue

            all_pages_text.append((i + 1, text))

            text_lower = text.lower()
            if any(keyword in text_lower for keyword in FINANCIAL_KEYWORDS):
                financial_pages.append((i + 1, text))

    print(f"Financial statement pages found: {len(financial_pages)}")

    if not financial_pages:
        print("Warning: no financial pages detected — using last 60 pages as fallback")
        financial_pages = all_pages_text[-60:]

    financial_pages = financial_pages[:40]

    combined_text = ""
    for page_num, text in financial_pages:
        combined_text += f"\n\n--- PAGE {page_num} ---\n\n"
        combined_text += text

    print(f"Extracted {len(combined_text):,} characters from financial pages")
    return combined_text


def get_pdf_info(pdf_path: str) -> dict:
    """Returns basic info about the PDF for display purposes."""
    with pdfplumber.open(pdf_path) as pdf:
        return {
            "total_pages": len(pdf.pages),
            "file_name": Path(pdf_path).name,
            "file_size_mb": round(Path(pdf_path).stat().st_size / 1_000_000, 2),
        }