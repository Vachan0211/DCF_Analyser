from engine.assumptions import DCFAssumptions
from parser.schemas import FinancialData


def calculate_wacc(data: FinancialData, assumptions: DCFAssumptions) -> dict:
    """
    Calculates WACC using CAPM for cost of equity and
    interest expense / total debt for pre-tax cost of debt.
    Matches the methodology from your HD Excel model.
    """
    # Cost of equity via CAPM
    cost_of_equity = assumptions.cost_of_equity()

    # Pre-tax cost of debt: interest expense / total debt
    total_debt = (
        data.balance_sheet.short_term_debt +
        data.balance_sheet.long_term_debt
    )
    if total_debt > 0:
        pre_tax_cost_of_debt = (
            data.income_statement.interest_expense / total_debt
        )
    else:
        pre_tax_cost_of_debt = 0.0

    after_tax_cost_of_debt = assumptions.after_tax_cost_of_debt(
        pre_tax_cost_of_debt
    )

    # Capital structure weights
    total_capital = assumptions.market_cap + total_debt
    weight_equity = assumptions.market_cap / total_capital
    weight_debt = total_debt / total_capital

    # WACC
    wacc = (
        weight_equity * cost_of_equity +
        weight_debt * after_tax_cost_of_debt
    )

    return {
        "cost_of_equity": round(cost_of_equity, 4),
        "pre_tax_cost_of_debt": round(pre_tax_cost_of_debt, 4),
        "after_tax_cost_of_debt": round(after_tax_cost_of_debt, 4),
        "weight_equity": round(weight_equity, 4),
        "weight_debt": round(weight_debt, 4),
        "total_debt": round(total_debt, 1),
        "wacc": round(wacc, 4),
    }