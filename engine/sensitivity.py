from engine.assumptions import DCFAssumptions
from engine.dcf import calculate_dcf
from parser.schemas import FinancialData


def run_sensitivity(
    data: FinancialData,
    assumptions: DCFAssumptions,
    wacc_range: list = None,
    growth_range: list = None,
) -> dict:
    """
    Builds a 2D sensitivity table of intrinsic value per share
    across a range of WACC and terminal growth rate assumptions.
    All keys stored as floats to avoid string/float mismatch.
    """
    if wacc_range is None:
        wacc_range = [0.06, 0.07, 0.08, 0.09, 0.10, 0.11]
    if growth_range is None:
        growth_range = [0.01, 0.02, 0.03, 0.04, 0.05]

    # Store as nested dicts with float keys
    table = {}

    for g in growth_range:
        row = {}
        for w in wacc_range:
            test_assumptions = DCFAssumptions(
                risk_free_rate=assumptions.risk_free_rate,
                equity_risk_premium=assumptions.equity_risk_premium,
                beta=assumptions.beta,
                tax_rate=assumptions.tax_rate,
                revenue_growth_rates=assumptions.revenue_growth_rates,
                gross_profit_margin=assumptions.gross_profit_margin,
                sg_and_a_pct=assumptions.sg_and_a_pct,
                capex_pct=assumptions.capex_pct,
                terminal_growth_rate=g,
                projection_years=assumptions.projection_years,
                market_cap=assumptions.market_cap,
                total_debt=assumptions.total_debt,
            )

            result     = calculate_dcf(data, test_assumptions)
            projections = result["projections"]

            pv_fcfs = []
            for i, proj in enumerate(projections):
                pv = proj["fcf"] / ((1 + w) ** (i + 1))
                pv_fcfs.append(pv)

            final_fcf = projections[-1]["fcf"]
            tv        = final_fcf * (1 + g) / (w - g)
            pv_tv     = tv / ((1 + w) ** assumptions.projection_years)

            ev        = sum(pv_fcfs) + pv_tv
            net_debt  = result["net_debt"]
            eq_val    = ev - net_debt
            per_share = round(
                eq_val / data.company_info.shares_outstanding, 2
            )

            row[round(w, 2)] = per_share
        table[round(g, 2)] = row

    return {
        "wacc_range":   [round(w, 2) for w in wacc_range],
        "growth_range": [round(g, 2) for g in growth_range],
        "table":        table,
    }