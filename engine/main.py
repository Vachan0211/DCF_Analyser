import json
from pathlib import Path
from parser.schemas import FinancialData
from engine.assumptions import DCFAssumptions
from engine.dcf import calculate_dcf
from engine.sensitivity import run_sensitivity
from engine.cca import run_cca


def run_engine(financial_data: FinancialData) -> dict:
    """
    Full DCF engine pipeline:
    1. Load assumptions
    2. Run DCF valuation
    3. Run sensitivity analysis
    4. Run comparable company analysis
    """
    print("\n" + "="*60)
    print("  DCF ENGINE")
    print("="*60)

    assumptions = DCFAssumptions()

    # DCF
    print("\n[Step 1/3] Running DCF valuation...")
    dcf_results = calculate_dcf(financial_data, assumptions)

    wacc = dcf_results["wacc_results"]["wacc"]
    iv = dcf_results["intrinsic_value_per_share"]

    print(f"  WACC:                    {wacc*100:.2f}%")
    print(f"  Enterprise Value:        ${dcf_results['enterprise_value']:>12,.1f}M")
    print(f"  Equity Value:            ${dcf_results['equity_value']:>12,.1f}M")
    print(f"  Intrinsic Value/Share:   ${iv:>10.2f}")

    # Sensitivity
    print("\n[Step 2/3] Running sensitivity analysis...")
    sensitivity = run_sensitivity(financial_data, assumptions)
    print("  Sensitivity table (intrinsic value per share):")
    print(f"  {'Growth':>8}", end="")
    for w in sensitivity["wacc_range"]:
        print(f"  WACC={w:.0%}", end="")
    print()
    for g in sensitivity["growth_range"]:
        print(f"  {g:.0%}    ", end="")
        for w in sensitivity["wacc_range"]:
            val = sensitivity["table"][g][w]
            print(f"  ${val:>7.0f}", end="")
        print()

    # CCA
    print("\n[Step 3/3] Running comparable company analysis...")
    cca_results = run_cca(financial_data)
    if "error" not in cca_results:
        print("  Median peer multiples:")
        m = cca_results["median_multiples"]
        print(f"    EV/Revenue:  {m['ev_revenue']:.1f}x")
        print(f"    EV/EBITDA:   {m['ev_ebitda']:.1f}x")
        print(f"    P/E:         {m['pe_ratio']:.1f}x")
        print("  Implied value per share:")
        iv2 = cca_results["implied_value_per_share"]
        print(f"    From EV/Revenue:  ${iv2['from_ev_revenue']:,.2f}")
        print(f"    From EV/EBITDA:   ${iv2['from_ev_ebitda']:,.2f}")
        print(f"    From P/E:         ${iv2['from_pe']:,.2f}")

    # Save results
    results = {
        "dcf": dcf_results,
        "sensitivity": sensitivity,
        "cca": cca_results,
    }
    output_path = Path("data") / f"{financial_data.company_info.ticker}_dcf_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to {output_path}")

    return results


if __name__ == "__main__":
    # Load the extracted financial data from Phase 2
    data_path = Path("data/HD_extracted.json")
    if not data_path.exists():
        print("HD_extracted.json not found. Run the parser first.")
        exit(1)

    with open(data_path) as f:
        raw = json.load(f)

    financial_data = FinancialData(**raw)
    run_engine(financial_data)