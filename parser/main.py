import json
from pathlib import Path
from parser.pdf_extractor import extract_financial_pages, get_pdf_info
from parser.llm_parser import parse_financials_with_llm
from parser.reviewer import display_extracted_data
from parser.schemas import FinancialData


def run_parser(pdf_path: str) -> FinancialData | None:
    """
    Full pipeline: PDF → text extraction → LLM parsing
    → human review → validated FinancialData object.
    Returns None if user rejects the extracted data.
    """
    print("\n" + "="*60)
    print("  DCF ANALYZER — 10-K PARSER")
    print("="*60)

    info = get_pdf_info(pdf_path)
    print(f"\n  File:  {info['file_name']}")
    print(f"  Size:  {info['file_size_mb']} MB")
    print(f"  Pages: {info['total_pages']}")

    print("\n[Step 1/3] Extracting financial statement pages...")
    extracted_text = extract_financial_pages(pdf_path)

    print("\n[Step 2/3] Parsing with Claude API...")
    financial_data = parse_financials_with_llm(extracted_text)

    print("\n[Step 3/3] Human review...")
    confirmed = display_extracted_data(financial_data)

    if not confirmed:
        print("\nExtraction rejected. Please check the PDF and try again.")
        return None

    output_path = Path("data") / f"{financial_data.company_info.ticker}_extracted.json"
    with open(output_path, "w") as f:
        json.dump(financial_data.model_dump(), f, indent=2)
    print(f"\nData saved to {output_path}")

    return financial_data


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        pdf_path = "data/HD_10K_2024.pdf"
        print(f"No PDF path provided — using default: {pdf_path}")
    else:
        pdf_path = sys.argv[1]

    result = run_parser(pdf_path)

    if result:
        print(f"\nParser complete. Ready for Phase 3 (DCF engine).")