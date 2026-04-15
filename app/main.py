import os
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

    st.subheader("API Configuration")
    user_api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-api03-...",
        help=(
            "Your key is never stored or shared. "
            "Get one free at console.anthropic.com — "
            "this project costs under $0.10 per run."
        )
    )

    if user_api_key:
        os.environ["ANTHROPIC_API_KEY"] = user_api_key
        st.success("API key ready.")
    else:
        st.warning(
            "Enter your Anthropic API key to use the parser. "
            "Your key is only used for this session and is "
            "never saved or shared."
        )

    st.divider()
    st.markdown("**How it works:**")
    st.markdown("1. Enter your API key above")
    st.markdown("2. Upload a 10-K PDF")
    st.markdown("3. Review extracted numbers")
    st.markdown("4. Adjust assumptions")
    st.markdown("5. Get valuation + charts")
    st.markdown("6. Download Excel + PDF")
    st.divider()

    st.markdown("**Cost per run:** ~$0.05")
    st.markdown(
        "Get an API key at "
        "[console.anthropic.com](https://console.anthropic.com)"
    )
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

# ── Gate: require API key before showing anything ─────────────
if not user_api_key:
    st.title("DCF Analyzer")
    st.markdown(
        "### Automated DCF valuation from any SEC 10-K filing"
    )
    st.markdown(
        "This tool extracts financial statements from any 10-K PDF "
        "using Claude AI, then builds a complete DCF valuation with "
        "sensitivity analysis, comparable company analysis, and "
        "downloadable Excel and PDF reports."
    )

    col1, col2, col3 = st.columns(3)
    col1.info("**Step 1**\nUpload any SEC 10-K PDF")
    col2.info("**Step 2**\nReview + adjust assumptions")
    col3.info("**Step 3**\nDownload Excel + PDF report")

    st.divider()
    st.markdown(
        "**To get started:** enter your Anthropic API key in the "
        "sidebar on the left. "
        "You can get a free key at "
        "[console.anthropic.com](https://console.anthropic.com). "
        "Each run costs approximately $0.05 in API credits."
    )
    st.info(
        "Your API key is used only for this browser session. "
        "It is never stored, logged, or shared."
    )
    st.stop()

# ── Main flow (only reached if API key is entered) ────────────
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

    if st.button("Run Valuation Model", type="primary"):
        with st.spinner("Running DCF engine..."):
            peer_tickers = st.session_state.get(
                "peer_tickers", ["LOW", "TSCO", "FND", "FERG"]
            )
            dcf_results = calculate_dcf(data, assumptions)
            sensitivity = run_sensitivity(data, assumptions)
            cca_results = run_cca(
                data,
                peer_tickers=peer_tickers
            )
            results = {
                "dcf":         dcf_results,
                "sensitivity": sensitivity,
                "cca":         cca_results,
            }
            st.session_state["results"] = results
            st.success("Model complete. Scroll down to see results.")

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