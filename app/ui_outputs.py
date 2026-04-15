import streamlit as st
import json
import tempfile
import os
from pathlib import Path
from outputs.excel_generator import generate_excel
from outputs.pdf_generator import generate_pdf


def render_outputs(data, results: dict):
    """
    Step 4: Generate and download Excel + PDF outputs.
    """
    st.header("Step 4 — Download Reports")
    st.markdown(
        "Your valuation model is ready. Download the full Excel "
        "workbook and the PDF executive summary below."
    )

    ticker = data.company_info.ticker

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Excel Workbook")
        st.markdown(
            "Three formatted sheets: DCF valuation, "
            "sensitivity analysis, and comparable companies."
        )
        if st.button("Generate Excel", type="primary",
                     use_container_width=True):
            with st.spinner("Building Excel workbook..."):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    path = os.path.join(
                        tmp_dir, f"{ticker}_DCF_Model.xlsx"
                    )
                    generate_excel(data, results,
                                   output_path=path)
                    with open(path, "rb") as f:
                        excel_bytes = f.read()

            st.download_button(
                label="Download Excel",
                data=excel_bytes,
                file_name=f"{ticker}_DCF_Model.xlsx",
                mime=("application/vnd.openxmlformats-"
                      "officedocument.spreadsheetml.sheet"),
                use_container_width=True
            )

    with c2:
        st.subheader("PDF Summary")
        st.markdown(
            "Two-page executive summary with valuation overview, "
            "assumptions table, sensitivity, and CCA."
        )
        if st.button("Generate PDF", type="primary",
                     use_container_width=True):
            with st.spinner("Building PDF summary..."):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    path = os.path.join(
                        tmp_dir, f"{ticker}_DCF_Summary.pdf"
                    )
                    generate_pdf(data, results,
                                 output_path=path)
                    with open(path, "rb") as f:
                        pdf_bytes = f.read()

            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=f"{ticker}_DCF_Summary.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    st.divider()

    # Raw JSON download for developers
    with st.expander("Download Raw JSON (for developers)"):
        st.download_button(
            label="Download results.json",
            data=json.dumps(results, indent=2),
            file_name=f"{ticker}_dcf_results.json",
            mime="application/json"
        )