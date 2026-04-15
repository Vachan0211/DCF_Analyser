import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def render_results(results: dict, data):
    """
    Step 3: Show DCF results, FCF chart,
    sensitivity heatmap, and CCA comparison.
    """
    st.header("Step 3 — Valuation Results")

    dcf    = results["dcf"]
    wacc_r = dcf["wacc_results"]
    projs  = dcf["projections"]
    iv     = dcf["intrinsic_value_per_share"]

    # ── Key metrics banner ────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("WACC",
              f"{wacc_r['wacc']*100:.2f}%",
              help="Weighted average cost of capital")
    c2.metric("Enterprise Value",
              f"${dcf['enterprise_value']:,.0f}M")
    c3.metric("Equity Value",
              f"${dcf['equity_value']:,.0f}M")
    c4.metric("Intrinsic Value / Share",
              f"${iv:,.2f}")

    st.divider()

    # ── FCF chart ─────────────────────────────────────────────
    st.subheader("Free Cash Flow Projections")

    years   = [str(p["year"]) for p in projs]
    fcfs    = [p["fcf"]       for p in projs]
    pv_fcfs = [p["pv_fcf"]   for p in projs]

    fig_fcf = go.Figure()
    fig_fcf.add_trace(go.Bar(
        name="FCF", x=years, y=fcfs,
        marker_color="#2E75B6",
        text=[f"${v:,.0f}" for v in fcfs],
        textposition="outside"
    ))
    fig_fcf.add_trace(go.Bar(
        name="PV of FCF", x=years, y=pv_fcfs,
        marker_color="#D6E4F0",
        text=[f"${v:,.0f}" for v in pv_fcfs],
        textposition="outside"
    ))
    fig_fcf.update_layout(
        barmode="group",
        xaxis_title="Year",
        yaxis_title="$ millions",
        legend=dict(orientation="h", y=1.1),
        margin=dict(t=40, b=40),
        height=380,
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#F0F0F0")
    )
    st.plotly_chart(fig_fcf, use_container_width=True)

    # Projection table
    with st.expander("Detailed Projection Table"):
        df = pd.DataFrame(projs)
        df = df[[
            "year", "revenue", "ebit", "nopat",
            "da", "capex", "change_in_nwc", "fcf", "pv_fcf"
        ]]
        df.columns = [
            "Year", "Revenue", "EBIT", "NOPAT",
            "D&A", "Capex", "ΔW/C", "FCF", "PV FCF"
        ]
        df = df.set_index("Year")
        st.dataframe(
            df.style.format("${:,.1f}"),
            use_container_width=True
        )

    st.divider()

    # ── Sensitivity heatmap ───────────────────────────────────
    st.subheader("Sensitivity Analysis")
    st.caption(
        "Intrinsic value per share across WACC and terminal "
        "growth rate combinations. Base case highlighted."
    )

    sens   = results["sensitivity"]
    w_list = sens["wacc_range"]
    g_list = sens["growth_range"]
    table  = sens["table"]

    # Robust key lookup — handles both string and float keys
    def _get(g, w):
        sg, sw = str(round(g, 2)), str(round(w, 2))
        row = table.get(sg, table.get(round(g, 2), {}))
        return row.get(sw, row.get(round(w, 2), 0))

    z        = [[_get(g, w) for w in w_list] for g in g_list]
    x_labels = [f"{w:.0%}" for w in w_list]
    y_labels = [f"{g:.0%}" for g in g_list]

    fig_heat = go.Figure(go.Heatmap(
        z=z, x=x_labels, y=y_labels,
        colorscale=[
            [0.0, "#FFCCCC"],
            [0.4, "#FFFFFF"],
            [1.0, "#E2EFDA"],
        ],
        text=[[f"${v:,.0f}" for v in row] for row in z],
        texttemplate="%{text}",
        textfont={"size": 11},
        showscale=True,
        colorbar=dict(title="$/share")
    ))
    fig_heat.update_layout(
        xaxis_title="WACC",
        yaxis_title="Terminal Growth Rate",
        height=320,
        margin=dict(t=20, b=40)
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()

    # ── WACC breakdown ────────────────────────────────────────
    st.subheader("WACC Breakdown")
    c1, c2, c3 = st.columns(3)
    c1.metric("Cost of Equity",
              f"{wacc_r['cost_of_equity']*100:.2f}%",
              help="CAPM: Rf + β × ERP")
    c2.metric("After-Tax Cost of Debt",
              f"{wacc_r['after_tax_cost_of_debt']*100:.2f}%")
    c3.metric("Equity Weight",
              f"{wacc_r['weight_equity']*100:.1f}%")

    st.divider()

    # ── CCA ───────────────────────────────────────────────────
    st.subheader("Comparable Company Analysis")

    cca = results.get("cca", {})
    if "error" not in cca and cca.get("peers"):
        peers = cca["peers"]
        med   = cca["median_multiples"]
        iv_c  = cca["implied_value_per_share"]

        df_peers = pd.DataFrame([{
            "Company":    p.get("name", p["ticker"]),
            "Ticker":     p["ticker"],
            "EV/Revenue": round(p.get("ev_revenue", 0), 1),
            "EV/EBITDA":  round(p.get("ev_ebitda",  0), 1),
            "P/E":        round(p.get("pe_ratio",   0), 1),
        } for p in peers])

        st.dataframe(
            df_peers.set_index("Ticker"),
            use_container_width=True
        )

        st.markdown(
            f"**Peer Medians:** "
            f"EV/Revenue {med['ev_revenue']:.1f}x  ·  "
            f"EV/EBITDA {med['ev_ebitda']:.1f}x  ·  "
            f"P/E {med['pe_ratio']:.1f}x"
        )

        # Implied vs DCF bar chart
        methods = ["EV/Revenue", "EV/EBITDA", "P/E", "DCF"]
        values  = [
            iv_c["from_ev_revenue"],
            iv_c["from_ev_ebitda"],
            iv_c["from_pe"],
            iv,
        ]
        colours = ["#D6E4F0", "#D6E4F0", "#D6E4F0", "#1F3864"]

        fig_cca = go.Figure(go.Bar(
            x=methods, y=values,
            marker_color=colours,
            text=[f"${v:,.2f}" for v in values],
            textposition="outside"
        ))
        fig_cca.update_layout(
            yaxis_title="Implied Value per Share ($)",
            height=340,
            margin=dict(t=40, b=20),
            plot_bgcolor="white",
            yaxis=dict(gridcolor="#F0F0F0")
        )
        st.plotly_chart(fig_cca, use_container_width=True)

    else:
        st.info(
            "CCA data unavailable — peer data could not be fetched. "
            "Check your network connection or enter peer tickers manually."
        )