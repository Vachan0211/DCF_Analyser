import json
from pathlib import Path
from parser.schemas import FinancialData
from outputs.excel_generator import generate_excel
from outputs.pdf_generator import generate_pdf


def generate_outputs(
    financial_data: FinancialData,
    results: dict,
    ticker: str = None
) -> dict:
    """
    Generates both Excel and PDF outputs from DCF results.
    Returns paths to both files.
    """
    print("\n" + "="*60)
    print("  OUTPUT GENERATOR")
    print("="*60)

    t = ticker or financial_data.company_info.ticker

    print("\n[Step 1/2] Generating Excel workbook...")
    excel_path = generate_excel(
        financial_data, results,
        output_path=f"outputs/{t}_DCF_Model.xlsx"
    )

    print("\n[Step 2/2] Generating PDF summary...")
    pdf_path = generate_pdf(
        financial_data, results,
        output_path=f"outputs/{t}_DCF_Summary.pdf"
    )

    print(f"\n  Done. Files saved to outputs/")
    return {
        "excel": excel_path,
        "pdf": pdf_path,
    }


if __name__ == "__main__":
    # Load saved results from Phase 2 + 3
    data_path    = Path("data/HD_extracted.json")
    results_path = Path("data/HD_dcf_results.json")

    if not data_path.exists() or not results_path.exists():
        print("Run parser and engine first.")
        exit(1)

    with open(data_path) as f:
        financial_data = FinancialData(**json.load(f))

    with open(results_path) as f:
        results = json.load(f)

    generate_outputs(financial_data, results)