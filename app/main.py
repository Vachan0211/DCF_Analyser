import streamlit as st
from engine.dcf import calculate_dcf
from engine.sensitivity import run_sensitivity
from engine.cca import run_cca

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="DCF Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.title("DCF Analyzer")
    st.markdown(
        "An automated valuation tool that extracts financial "
        "data from any SEC 10-K filing and builds a full DCF model."
    )
    st.divider()
    st.markdown("**How it works:**")
    st.markdown("1. Upload a 10-K PDF")
    st.markdown("2. Review extracted numbers")
    st.markdown("3. Adjust assumptions")
    st.markdown("4. Get valuation + charts")
    st.markdown("5. Download Excel + PDF")
    st.divider()
    st.caption(
        "Built with Python · Claude API · Streamlit · Plotly"
    )

# ── Session state init ────────────────────────────────────────
if "extraction_done" not in st.session_state:
    st.session_state["extraction_done"] = False
if "model_ready" not in st.session_state:
    st.session_state["model_ready"] = False
if "results" not in st.session_state:
    st.session_state["results"] = None

# ── Main flow ─────────────────────────────────────────────────
from app.ui_parser      import render_parser
from app.ui_assumptions import render_assumptions
from app.ui_results     import render_results
from app.ui_outputs     import render_outputs

# Step 1: Parse
render_parser()

# Step 2: Assumptions (only if data confirmed)
if st.session_state.get("model_ready"):
    data        = st.session_state["confirmed_data"]
    assumptions = render_assumptions(data)

    st.divider()

    # Run model button
    if st.button("Run Valuation Model", type="primary"):
        with st.spinner("Running DCF engine..."):
            peer_tickers = st.session_state.get(
                "peer_tickers", ["LOW","TSCO","FND","FERG"]
            )
            dcf_results  = calculate_dcf(data, assumptions)
            sensitivity  = run_sensitivity(data, assumptions)
            cca_results  = run_cca(
    data,
    peer_tickers=peer_tickers
)
            results = {
                "dcf":         dcf_results,
                "sensitivity": sensitivity,
                "cca":         cca_results,
            }
            st.session_state["results"] = results
            st.success("Model complete.")

    # Step 3: Results
    if st.session_state["results"]:
        st.divider()
        render_results(
            st.session_state["results"],
            data
        )
        st.divider()

        # Step 4: Outputs
        render_outputs(data, st.session_state["results"])