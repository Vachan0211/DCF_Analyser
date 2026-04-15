import streamlit as st
import tempfile
import os
from parser.pdf_extractor import extract_financial_pages, get_pdf_info
from parser.llm_parser import parse_financials_with_llm
from parser.schemas import FinancialData


def render_parser():
    """
    Step 1: Upload a 10-K PDF, extract financial data,
    allow user to review and edit before proceeding.
    """
    st.header("Step 1 — Upload 10-K Filing")
    st.markdown(
        "Upload any SEC 10-K annual report PDF. The parser will "
        "automatically identify the financial statement pages and "
        "extract key figures using Claude AI."
    )

    uploaded_file = st.file_uploader(
        "Drop your 10-K PDF here",
        type=["pdf"],
        help="Annual reports (10-K) from SEC EDGAR or company IR pages"
    )

    if uploaded_file is None:
        st.info(
            "No file uploaded yet. You can download a 10-K from "
            "[SEC EDGAR](https://www.sec.gov/cgi-bin/browse-edgar) "
            "or the company's investor relations page."
        )
        return None

    # Save to temp file
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".pdf"
    ) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        info = get_pdf_info(tmp_path)

        # Use original filename not the temp file name
        original_name = uploaded_file.name
        display_name  = (original_name[:28] + "..."
                         if len(original_name) > 28
                         else original_name)

        col1, col2, col3 = st.columns(3)
        col1.metric("File",  display_name)
        col2.metric("Pages", info["total_pages"])
        col3.metric("Size",  f"{info['file_size_mb']} MB")

        if st.button("Extract Financial Data", type="primary"):
            with st.spinner(
                "Scanning financial statement pages..."
            ):
                extracted_text = extract_financial_pages(tmp_path)

            with st.spinner(
                "Claude is reading the filing — this takes "
                "about 20–30 seconds..."
            ):
                try:
                    financial_data = parse_financials_with_llm(
                        extracted_text
                    )
                    st.session_state["financial_data"] = financial_data
                    st.session_state["extraction_done"] = True
                    st.success(
                        "Extraction complete — review the "
                        "numbers below."
                    )
                except ValueError as e:
                    st.error(f"Extraction failed: {e}")
                    st.info(
                        "Tips: Make sure the PDF is a standard "
                        "10-K filing and not password protected. "
                        "Very large PDFs (200+ pages) may need "
                        "to be trimmed to financial sections only."
                    )
                    return None

    finally:
        os.unlink(tmp_path)

    if st.session_state.get("extraction_done"):
        return _review_screen(st.session_state["financial_data"])

    return None


def _review_screen(data: FinancialData) -> FinancialData:
    """
    Shows extracted numbers in editable fields.
    User confirms before the model runs.
    """
    st.divider()
    st.subheader("Review Extracted Data")
    st.markdown(
        "Check the numbers below against the original filing. "
        "Edit any incorrect values before running the model."
    )

    info = data.company_info
    inc  = data.income_statement
    bal  = data.balance_sheet
    cf   = data.cash_flow_statement

    # Company info
    with st.expander("Company Info", expanded=True):
        c1, c2, c3 = st.columns(3)
        company_name    = c1.text_input("Company Name",
                                        value=info.company_name)
        ticker          = c2.text_input("Ticker",
                                        value=info.ticker)
        fiscal_year     = c3.number_input("Fiscal Year",
                                          value=info.fiscal_year,
                                          step=1)
        c4, c5 = st.columns(2)
        fiscal_year_end = c4.text_input("Fiscal Year End",
                                        value=info.fiscal_year_end_date)
        shares          = c5.number_input(
                            "Shares Outstanding (M)",
                            value=float(info.shares_outstanding),
                            step=0.1)

    # Income statement
    with st.expander("Income Statement ($ millions)",
                     expanded=True):
        c1, c2 = st.columns(2)
        revenue  = c1.number_input("Revenue",
                                   value=float(inc.revenue),
                                   step=1.0, format="%.1f")
        cos      = c2.number_input("Cost of Sales",
                                   value=float(inc.cost_of_sales),
                                   step=1.0, format="%.1f")
        gp       = c1.number_input("Gross Profit",
                                   value=float(inc.gross_profit),
                                   step=1.0, format="%.1f")
        sga      = c2.number_input("SG&A",
                                   value=float(inc.sg_and_a),
                                   step=1.0, format="%.1f")
        da       = c1.number_input(
                    "D&A",
                    value=float(inc.depreciation_and_amortization),
                    step=1.0, format="%.1f")
        ebit     = c2.number_input("Operating Income (EBIT)",
                                   value=float(inc.operating_income),
                                   step=1.0, format="%.1f")
        int_exp  = c1.number_input("Interest Expense",
                                   value=float(inc.interest_expense),
                                   step=1.0, format="%.1f")
        int_inc  = c2.number_input("Interest Income",
                                   value=float(inc.interest_income),
                                   step=1.0, format="%.1f")
        pretax   = c1.number_input("Pre-Tax Income",
                                   value=float(inc.pre_tax_income),
                                   step=1.0, format="%.1f")
        tax      = c2.number_input("Tax Expense",
                                   value=float(inc.tax_expense),
                                   step=1.0, format="%.1f")
        net_inc  = c1.number_input("Net Income",
                                   value=float(inc.net_income),
                                   step=1.0, format="%.1f")

    # Balance sheet
    with st.expander("Balance Sheet ($ millions)",
                     expanded=True):
        c1, c2 = st.columns(2)
        cash    = c1.number_input(
                    "Cash & Equivalents",
                    value=float(bal.cash_and_equivalents),
                    step=1.0, format="%.1f")
        cur_ast = c2.number_input(
                    "Total Current Assets",
                    value=float(bal.total_current_assets),
                    step=1.0, format="%.1f")
        tot_ast = c1.number_input(
                    "Total Assets",
                    value=float(bal.total_assets),
                    step=1.0, format="%.1f")
        cur_lib = c2.number_input(
                    "Total Current Liabilities",
                    value=float(bal.total_current_liabilities),
                    step=1.0, format="%.1f")
        st_debt = c1.number_input(
                    "Short-Term Debt",
                    value=float(bal.short_term_debt),
                    step=1.0, format="%.1f")
        lt_debt = c2.number_input(
                    "Long-Term Debt",
                    value=float(bal.long_term_debt),
                    step=1.0, format="%.1f")
        tot_lib = c1.number_input(
                    "Total Liabilities",
                    value=float(bal.total_liabilities),
                    step=1.0, format="%.1f")
        equity  = c2.number_input(
                    "Total Equity",
                    value=float(bal.total_equity),
                    step=1.0, format="%.1f")

    # Cash flows
    with st.expander("Cash Flow Statement ($ millions)",
                     expanded=True):
        c1, c2, c3 = st.columns(3)
        op_cf   = c1.number_input(
                    "Operating Cash Flow",
                    value=float(cf.operating_cash_flow),
                    step=1.0, format="%.1f")
        capex   = c2.number_input(
                    "Capital Expenditures",
                    value=float(cf.capital_expenditures),
                    step=1.0, format="%.1f")
        da_cf   = c3.number_input(
                    "D&A (Cash Flow)",
                    value=float(cf.depreciation_and_amortization),
                    step=1.0, format="%.1f")

    if st.button("Confirm & Run Model", type="primary"):
        from parser.schemas import (
            CompanyInfo, IncomeStatement,
            BalanceSheet, CashFlowStatement
        )
        updated = FinancialData(
            company_info=CompanyInfo(
                company_name=company_name,
                ticker=ticker,
                fiscal_year=int(fiscal_year),
                fiscal_year_end_date=fiscal_year_end,
                shares_outstanding=shares,
            ),
            income_statement=IncomeStatement(
                revenue=revenue,
                cost_of_sales=cos,
                gross_profit=gp,
                sg_and_a=sga,
                depreciation_and_amortization=da,
                operating_income=ebit,
                interest_expense=int_exp,
                interest_income=int_inc,
                pre_tax_income=pretax,
                tax_expense=tax,
                net_income=net_inc,
            ),
            balance_sheet=BalanceSheet(
                cash_and_equivalents=cash,
                total_current_assets=cur_ast,
                total_assets=tot_ast,
                total_current_liabilities=cur_lib,
                short_term_debt=st_debt,
                long_term_debt=lt_debt,
                total_liabilities=tot_lib,
                total_equity=equity,
            ),
            cash_flow_statement=CashFlowStatement(
                operating_cash_flow=op_cf,
                capital_expenditures=capex,
                depreciation_and_amortization=da_cf,
            ),
        )
        st.session_state["confirmed_data"] = updated
        st.session_state["model_ready"]    = True
        st.success("Data confirmed. Scroll down to Step 2.")
        return updated

    return None