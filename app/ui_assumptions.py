import streamlit as st
from engine.assumptions import DCFAssumptions


def render_assumptions(data) -> DCFAssumptions:
    """
    Step 2: Let user adjust all DCF assumptions via sliders.
    Returns a DCFAssumptions object with the selected values.
    """
    st.header("Step 2 — Set Assumptions")
    st.markdown(
        "Adjust the inputs below. The model will recalculate "
        "instantly when you run it."
    )

    # Auto-derive market cap suggestion from data
    total_debt = (
        data.balance_sheet.short_term_debt +
        data.balance_sheet.long_term_debt
    )

    tab1, tab2, tab3 = st.tabs(
        ["WACC Inputs", "Revenue & Margins", "DCF Settings"]
    )

    with tab1:
        st.subheader("WACC Inputs")
        c1, c2 = st.columns(2)
        risk_free = c1.slider(
            "Risk-Free Rate (%)",
            min_value=2.0, max_value=6.0, value=4.11, step=0.01,
            help="Yield on 10-year US Treasury"
        ) / 100
        erp = c2.slider(
            "Equity Risk Premium (%)",
            min_value=3.0, max_value=7.0, value=4.46, step=0.01,
            help="Damodaran market ERP"
        ) / 100
        beta = c1.slider(
            "Beta",
            min_value=0.5, max_value=2.0, value=1.04, step=0.01,
            help="Company beta vs market"
        )
        tax_rate = c2.slider(
            "Tax Rate (%)",
            min_value=15.0, max_value=35.0, value=24.0, step=0.5,
            help="Effective corporate tax rate"
        ) / 100

        st.subheader("Capital Structure")
        c3, c4 = st.columns(2)
        market_cap = c3.number_input(
            "Market Cap ($ millions)",
            value=351973.0, step=1000.0, format="%.0f",
            help="Current market capitalisation"
        )
        debt_input = c4.number_input(
            "Total Debt ($ millions)",
            value=float(round(total_debt)),
            step=100.0, format="%.0f",
            help="Short-term + long-term debt from balance sheet"
        )

        # Live WACC preview
        coe   = risk_free + beta * erp
        cod   = (data.income_statement.interest_expense /
                 debt_input) * (1 - tax_rate) if debt_input > 0 else 0
        w_eq  = market_cap / (market_cap + debt_input)
        w_d   = debt_input / (market_cap + debt_input)
        wacc_preview = w_eq * coe + w_d * cod

        st.info(
            f"**Estimated WACC: {wacc_preview*100:.2f}%** "
            f"(Cost of Equity: {coe*100:.2f}%  ·  "
            f"After-Tax Cost of Debt: {cod*100:.2f}%)"
        )

    with tab2:
        st.subheader("Revenue Growth Rates")
        c1, c2, c3 = st.columns(3)
        g1 = c1.slider("Year 1 (%)", 0.0, 15.0, 4.0, 0.5) / 100
        g2 = c2.slider("Year 2 (%)", 0.0, 15.0, 4.0, 0.5) / 100
        g3 = c3.slider("Year 3 (%)", 0.0, 15.0, 3.5, 0.5) / 100
        c4, c5 = st.columns(2)
        g4 = c4.slider("Year 4 (%)", 0.0, 15.0, 3.0, 0.5) / 100
        g5 = c5.slider("Year 5 (%)", 0.0, 15.0, 3.0, 0.5) / 100

        st.subheader("Margin Assumptions")
        c6, c7, c8 = st.columns(3)
        gpm   = c6.slider(
            "Gross Profit Margin (%)",
            20.0, 60.0,
            round(data.income_statement.gross_profit /
                  data.income_statement.revenue * 100, 1),
            0.1
        ) / 100
        sga_p = c7.slider(
            "SG&A % of Revenue",
            5.0, 35.0,
            round(data.income_statement.sg_and_a /
                  data.income_statement.revenue * 100, 1),
            0.1
        ) / 100
        capex_p = c8.slider(
            "Capex % of Revenue",
            0.5, 8.0,
            round(data.cash_flow_statement.capital_expenditures /
                  data.income_statement.revenue * 100, 1),
            0.1
        ) / 100

    with tab3:
        st.subheader("DCF Settings")
        c1, c2 = st.columns(2)
        terminal_g = c1.slider(
            "Terminal Growth Rate (%)",
            0.5, 5.0, 2.0, 0.1,
            help="Long-run perpetual growth rate (Gordon Growth Model)"
        ) / 100
        proj_years = c2.select_slider(
            "Projection Period (years)",
            options=[3, 4, 5, 7, 10], value=5
        )

        st.subheader("Peer Tickers for CCA")
        st.markdown(
            "Enter 2–5 ticker symbols separated by commas. "
            "Live data will be fetched if your network allows it — "
            "otherwise the tool uses validated research data."
        )
        peers_input = st.text_input(
            "Peer Tickers",
            value="LOW, TSCO, FND, FERG",
            help="e.g. LOW, TSCO, FND, FERG"
        )
        peer_tickers = [t.strip().upper()
                        for t in peers_input.split(",")
                        if t.strip()]

    assumptions = DCFAssumptions(
        risk_free_rate=risk_free,
        equity_risk_premium=erp,
        beta=beta,
        tax_rate=tax_rate,
        revenue_growth_rates=[g1, g2, g3, g4, g5],
        gross_profit_margin=gpm,
        sg_and_a_pct=sga_p,
        capex_pct=capex_p,
        terminal_growth_rate=terminal_g,
        projection_years=proj_years,
        market_cap=market_cap,
        total_debt=debt_input,
    )

    st.session_state["peer_tickers"] = peer_tickers
    return assumptions