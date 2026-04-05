# Automated DCF Analyzer

A Python tool that accepts any SEC 10-K filing (PDF), extracts 
financial statements using an LLM, and produces a full DCF valuation 
with sensitivity analysis, comparable company analysis, an Excel model, 
and a PDF summary — all through an interactive Streamlit dashboard.

## Tech Stack
Python · pdfplumber · Anthropic API · pandas · yfinance · 
openpyxl · reportlab · Streamlit · Plotly

## Project Structure
- `parser/`  — 10-K PDF extraction and LLM normalization
- `engine/`  — WACC, FCF, DCF, CCA calculation logic
- `outputs/` — Excel and PDF report generation
- `app/`     — Streamlit web dashboard

## Setup
1. Clone the repo
2. Create a virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Add your Anthropic API key to `.env`
5. Run the app: `streamlit run app/main.py`

## Status
- [x] Phase 1: Project setup
- [ ] Phase 2: PDF parser
- [ ] Phase 3: DCF engine
- [ ] Phase 4: Output generation
- [ ] Phase 5: Streamlit dashboard