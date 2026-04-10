from parser.schemas import FinancialData


def display_extracted_data(data: FinancialData) -> bool:
    """
    Displays extracted financial data in a readable format
    and asks the user to confirm before proceeding.
    Returns True if confirmed, False if user wants to abort.
    """
    info = data.company_info
    inc = data.income_statement
    bal = data.balance_sheet
    cf = data.cash_flow_statement

    print("\n" + "="*60)
    print("  EXTRACTED FINANCIAL DATA — PLEASE REVIEW")
    print("="*60)

    print(f"\n  Company:          {info.company_name}")
    print(f"  Ticker:           {info.ticker}")
    print(f"  Fiscal Year:      {info.fiscal_year}")
    print(f"  Year End:         {info.fiscal_year_end_date}")
    print(f"  Shares Out (M):   {info.shares_outstanding:,.1f}")

    print(f"\n  --- Income Statement ($ millions) ---")
    print(f"  Revenue:              ${inc.revenue:>12,.1f}")
    print(f"  Cost of Sales:        ${inc.cost_of_sales:>12,.1f}")
    print(f"  Gross Profit:         ${inc.gross_profit:>12,.1f}")
    print(f"  SG&A:                 ${inc.sg_and_a:>12,.1f}")
    print(f"  D&A:                  ${inc.depreciation_and_amortization:>12,.1f}")
    print(f"  Operating Income:     ${inc.operating_income:>12,.1f}")
    print(f"  Interest Expense:     ${inc.interest_expense:>12,.1f}")
    print(f"  Interest Income:      ${inc.interest_income:>12,.1f}")
    print(f"  Pre-Tax Income:       ${inc.pre_tax_income:>12,.1f}")
    print(f"  Tax Expense:          ${inc.tax_expense:>12,.1f}")
    print(f"  Net Income:           ${inc.net_income:>12,.1f}")

    print(f"\n  --- Balance Sheet ($ millions) ---")
    print(f"  Cash:                 ${bal.cash_and_equivalents:>12,.1f}")
    print(f"  Current Assets:       ${bal.total_current_assets:>12,.1f}")
    print(f"  Total Assets:         ${bal.total_assets:>12,.1f}")
    print(f"  Current Liabilities:  ${bal.total_current_liabilities:>12,.1f}")
    print(f"  Short-Term Debt:      ${bal.short_term_debt:>12,.1f}")
    print(f"  Long-Term Debt:       ${bal.long_term_debt:>12,.1f}")
    print(f"  Total Liabilities:    ${bal.total_liabilities:>12,.1f}")
    print(f"  Total Equity:         ${bal.total_equity:>12,.1f}")

    print(f"\n  --- Cash Flow Statement ($ millions) ---")
    print(f"  Operating Cash Flow:  ${cf.operating_cash_flow:>12,.1f}")
    print(f"  Capital Expenditures: ${cf.capital_expenditures:>12,.1f}")
    print(f"  D&A (CF):             ${cf.depreciation_and_amortization:>12,.1f}")

    print("\n" + "="*60)
    print("  Compare these numbers against your HD Excel model.")
    print("  Revenue should be ~$159,514M, Net Income ~$14,806M")
    print("="*60)

    response = input("\n  Do these numbers look correct? (yes/no): ").strip().lower()
    return response in ("yes", "y")