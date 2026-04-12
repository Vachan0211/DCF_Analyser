from engine.assumptions import DCFAssumptions
from engine.wacc import calculate_wacc
from parser.schemas import FinancialData


def project_fcf(data: FinancialData, assumptions: DCFAssumptions) -> list:
    """
    Projects free cash flow for each forecast year.
    FCF = NOPAT + D&A - Capex - Change in Working Capital
    """
    base_revenue = data.income_statement.revenue
    base_nwc = (
        data.balance_sheet.total_current_assets -
        data.balance_sheet.total_current_liabilities
    )

    projections = []
    prev_revenue = base_revenue
    prev_nwc = base_nwc

    for i, growth_rate in enumerate(assumptions.revenue_growth_rates):
        year = data.company_info.fiscal_year + i + 1

        # Revenue
        revenue = prev_revenue * (1 + growth_rate)

        # Operating income (EBIT)
        gross_profit = revenue * assumptions.gross_profit_margin
        sg_and_a = revenue * assumptions.sg_and_a_pct
        ebit = gross_profit - sg_and_a

        # NOPAT (Net Operating Profit After Tax)
        nopat = ebit * (1 - assumptions.tax_rate)

        # D&A (grow with revenue)
        da_pct = (
            data.cash_flow_statement.depreciation_and_amortization /
            base_revenue
        )
        da = revenue * da_pct

        # Capex
        capex = revenue * assumptions.capex_pct

        # Change in Net Working Capital
        nwc = revenue * (base_nwc / base_revenue)
        change_in_nwc = nwc - prev_nwc

        # Free Cash Flow
        fcf = nopat + da - capex - change_in_nwc

        projections.append({
            "year": year,
            "revenue": round(revenue, 1),
            "ebit": round(ebit, 1),
            "nopat": round(nopat, 1),
            "da": round(da, 1),
            "capex": round(capex, 1),
            "change_in_nwc": round(change_in_nwc, 1),
            "fcf": round(fcf, 1),
        })

        prev_revenue = revenue
        prev_nwc = nwc

    return projections


def calculate_dcf(data: FinancialData, assumptions: DCFAssumptions) -> dict:
    """
    Full DCF: projects FCF, discounts to PV, adds terminal value,
    computes enterprise value and intrinsic value per share.
    """
    wacc_results = calculate_wacc(data, assumptions)
    wacc = wacc_results["wacc"]
    projections = project_fcf(data, assumptions)

    # Discount each FCF to present value
    pv_fcfs = []
    for i, proj in enumerate(projections):
        discount_factor = 1 / ((1 + wacc) ** (i + 1))
        pv = proj["fcf"] * discount_factor
        pv_fcfs.append(round(pv, 1))
        projections[i]["discount_factor"] = round(discount_factor, 4)
        projections[i]["pv_fcf"] = round(pv, 1)

    sum_pv_fcf = sum(pv_fcfs)

    # Terminal value (Gordon Growth Model)
    final_fcf = projections[-1]["fcf"]
    terminal_value = (
        final_fcf * (1 + assumptions.terminal_growth_rate) /
        (wacc - assumptions.terminal_growth_rate)
    )
    pv_terminal_value = terminal_value / (
        (1 + wacc) ** assumptions.projection_years
    )

    # Enterprise value
    enterprise_value = sum_pv_fcf + pv_terminal_value

    # Equity value
    net_debt = (
        wacc_results["total_debt"] -
        data.balance_sheet.cash_and_equivalents
    )
    equity_value = enterprise_value - net_debt

    # Intrinsic value per share
    shares = data.company_info.shares_outstanding
    intrinsic_value_per_share = equity_value / shares

    return {
        "wacc_results": wacc_results,
        "projections": projections,
        "sum_pv_fcf": round(sum_pv_fcf, 1),
        "terminal_value": round(terminal_value, 1),
        "pv_terminal_value": round(pv_terminal_value, 1),
        "enterprise_value": round(enterprise_value, 1),
        "net_debt": round(net_debt, 1),
        "equity_value": round(equity_value, 1),
        "shares_outstanding": shares,
        "intrinsic_value_per_share": round(intrinsic_value_per_share, 2),
    }