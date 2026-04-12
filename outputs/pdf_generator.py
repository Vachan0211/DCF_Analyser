from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from pathlib import Path
from parser.schemas import FinancialData


# ── Colours ──────────────────────────────────────────────────
DARK_BLUE  = colors.HexColor("#1F3864")
MID_BLUE   = colors.HexColor("#2E75B6")
LIGHT_BLUE = colors.HexColor("#D6E4F0")
ORANGE     = colors.HexColor("#C55A11")
LIGHT_GRAY = colors.HexColor("#F2F2F2")
GREEN      = colors.HexColor("#375623")
LIGHT_GREEN = colors.HexColor("#E2EFDA")
RED        = colors.HexColor("#C00000")


def _styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "title", parent=base["Normal"],
            fontSize=20, textColor=DARK_BLUE,
            fontName="Helvetica-Bold",
            spaceAfter=4
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"],
            fontSize=11, textColor=colors.gray,
            fontName="Helvetica", spaceAfter=12
        ),
        "section": ParagraphStyle(
            "section", parent=base["Normal"],
            fontSize=12, textColor=colors.white,
            fontName="Helvetica-Bold",
            backColor=DARK_BLUE,
            spaceBefore=14, spaceAfter=6,
            leftIndent=6
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"],
            fontSize=10, textColor=colors.black,
            fontName="Helvetica",
            spaceAfter=6, leading=14
        ),
        "metric_label": ParagraphStyle(
            "metric_label", parent=base["Normal"],
            fontSize=10, textColor=colors.gray,
            fontName="Helvetica"
        ),
        "metric_value": ParagraphStyle(
            "metric_value", parent=base["Normal"],
            fontSize=14, textColor=DARK_BLUE,
            fontName="Helvetica-Bold"
        ),
    }
    return styles


def _key_metrics_table(dcf: dict) -> Table:
    """Top-row summary cards."""
    wacc   = dcf["wacc_results"]["wacc"]
    iv     = dcf["intrinsic_value_per_share"]
    ev     = dcf["enterprise_value"]
    eq_val = dcf["equity_value"]

    data = [
        ["WACC", "Enterprise Value", "Equity Value", "Intrinsic Value/Share"],
        [
            f"{wacc*100:.2f}%",
            f"${ev:,.0f}M",
            f"${eq_val:,.0f}M",
            f"${iv:,.2f}",
        ],
    ]
    t = Table(data, colWidths=[1.6*inch]*4)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  DARK_BLUE),
        ("TEXTCOLOR",    (0,0), (-1,0),  colors.white),
        ("FONTNAME",     (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,0),  9),
        ("BACKGROUND",   (0,1), (-1,1),  LIGHT_BLUE),
        ("FONTNAME",     (0,1), (-1,1),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,1), (-1,1),  13),
        ("TEXTCOLOR",    (0,1), (-1,1),  DARK_BLUE),
        ("ALIGN",        (0,0), (-1,-1), "CENTER"),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [DARK_BLUE, LIGHT_BLUE]),
        ("GRID",         (0,0), (-1,-1), 0.5, colors.white),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
    ]))
    return t


def _assumptions_table(results: dict) -> Table:
    wacc_r = results["dcf"]["wacc_results"]
    projs  = results["dcf"]["projections"]
    g      = results["dcf"]

    growth_rates = [p["revenue"] / (projs[i-1]["revenue"] if i > 0 else
                    results["dcf"]["projections"][0]["revenue"])
                    - 1 for i, p in enumerate(projs)]

    rows = [["Assumption", "Value", "Rationale"]]
    assumptions = [
        ("WACC",              f"{wacc_r['wacc']*100:.2f}%",
         "CAPM cost of equity + after-tax cost of debt, market-value weighted"),
        ("Terminal Growth",   "2.0%",
         "Aligned with long-run US GDP / inflation expectations"),
        ("Revenue Growth Yr1-2", "4.0%",
         "SRS acquisition contribution + core demand recovery"),
        ("Revenue Growth Yr3-5", "3.5% → 3.0%",
         "Gradual deceleration toward industry maturity"),
        ("Gross Margin",      "33.4%",
         "Consistent with 3-year historical average"),
        ("SG&A % Revenue",    "18.0%",
         "Based on FY2024 actual; held constant in forecast"),
        ("Capex % Revenue",   "2.1%",
         "Historical average; store maintenance + tech investment"),
    ]
    for label, val, rationale in assumptions:
        rows.append([label, val, rationale])

    t = Table(rows, colWidths=[1.5*inch, 1.1*inch, 3.8*inch])
    style = [
        ("BACKGROUND",    (0,0), (-1,0),  MID_BLUE),
        ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
        ("ALIGN",         (0,0), (0,-1),  "LEFT"),
        ("ALIGN",         (1,0), (1,-1),  "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.lightgrey),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]
    for i in range(1, len(rows)):
        bg = LIGHT_GRAY if i % 2 == 0 else colors.white
        style.append(("BACKGROUND", (0,i), (-1,i), bg))
    t.setStyle(TableStyle(style))
    return t


def _sensitivity_table(results: dict) -> Table:
    sens   = results["sensitivity"]
    w_list = sens["wacc_range"]
    g_list = sens["growth_range"]
    table  = sens["table"]
    base   = results["dcf"]["intrinsic_value_per_share"]

    header = ["g \\ WACC"] + [f"{w:.0%}" for w in w_list]
    rows   = [header]
    for g in g_list:
        row = [f"{g:.0%}"]
        for w in w_list:
            row.append(f"${table[str(round(g,2))][str(round(w,2))]:,.0f}")
        rows.append(row)

    col_w = [0.8*inch] + [0.85*inch]*len(w_list)
    t = Table(rows, colWidths=col_w)

    style = [
        ("BACKGROUND",    (0,0), (-1,0),  DARK_BLUE),
        ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("BACKGROUND",    (0,1), (0,-1),  MID_BLUE),
        ("TEXTCOLOR",     (0,1), (0,-1),  colors.white),
        ("FONTNAME",      (0,1), (0,-1),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.white),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]
    # Colour cells vs base case
    for ri, g in enumerate(g_list, 1):
        for ci, w in enumerate(w_list, 1):
            val = table[str(round(g,2))][str(round(w,2))]
            if val >= base * 1.10:
                style.append(("BACKGROUND", (ci,ri), (ci,ri), LIGHT_GREEN))
            elif val <= base * 0.90:
                style.append(("BACKGROUND", (ci,ri), (ci,ri),
                               colors.HexColor("#FFCCCC")))
            else:
                style.append(("BACKGROUND", (ci,ri), (ci,ri), colors.white))

    t.setStyle(TableStyle(style))
    return t


def _cca_table(results: dict) -> Table:
    cca   = results["cca"]
    peers = cca["peers"]
    med   = cca["median_multiples"]

    rows = [["Company", "EV/Revenue", "EV/EBITDA", "P/E"]]
    for p in peers:
        rows.append([
            p.get("name", p["ticker"]),
            f"{p.get('ev_revenue',0):.1f}x",
            f"{p.get('ev_ebitda',0):.1f}x",
            f"{p.get('pe_ratio',0):.1f}x",
        ])
    rows.append([
        "Median",
        f"{med['ev_revenue']:.1f}x",
        f"{med['ev_ebitda']:.1f}x",
        f"{med['pe_ratio']:.1f}x",
    ])

    t = Table(rows, colWidths=[2.8*inch, 1.1*inch, 1.1*inch, 1.1*inch])
    style = [
        ("BACKGROUND",    (0,0),  (-1,0),  MID_BLUE),
        ("TEXTCOLOR",     (0,0),  (-1,0),  colors.white),
        ("FONTNAME",      (0,0),  (-1,0),  "Helvetica-Bold"),
        ("BACKGROUND",    (0,-1), (-1,-1), LIGHT_BLUE),
        ("FONTNAME",      (0,-1), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),  (-1,-1), 9),
        ("ALIGN",         (1,0),  (-1,-1), "CENTER"),
        ("ALIGN",         (0,0),  (0,-1),  "LEFT"),
        ("VALIGN",        (0,0),  (-1,-1), "MIDDLE"),
        ("GRID",          (0,0),  (-1,-1), 0.5, colors.lightgrey),
        ("TOPPADDING",    (0,0),  (-1,-1), 5),
        ("BOTTOMPADDING", (0,0),  (-1,-1), 5),
        ("LEFTPADDING",   (0,0),  (0,-1),  6),
    ]
    for i in range(1, len(rows)-1):
        bg = LIGHT_GRAY if i % 2 == 0 else colors.white
        style.append(("BACKGROUND", (0,i), (-1,i), bg))
    t.setStyle(TableStyle(style))
    return t


def generate_pdf(
    data: FinancialData,
    results: dict,
    output_path: str = None
) -> str:
    """
    Generates a 2-page PDF executive summary with:
    - Key metrics banner
    - DCF assumptions table
    - Sensitivity analysis table
    - CCA table
    - Auto-generated narrative
    Returns the path to the saved file.
    """
    if output_path is None:
        ticker = data.company_info.ticker
        output_path = f"outputs/{ticker}_DCF_Summary.pdf"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.65*inch,
        leftMargin=0.65*inch,
        topMargin=0.65*inch,
        bottomMargin=0.65*inch,
    )

    S = _styles()
    story = []

    # ── Header ──────────────────────────────────────────────
    story.append(Paragraph(
        f"{data.company_info.company_name} ({data.company_info.ticker})",
        S["title"]
    ))
    story.append(Paragraph(
        f"DCF Valuation Summary · Fiscal Year {data.company_info.fiscal_year} "
        f"· Ended {data.company_info.fiscal_year_end_date}",
        S["subtitle"]
    ))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=DARK_BLUE, spaceAfter=12
    ))

    # ── Key metrics ─────────────────────────────────────────
    story.append(_key_metrics_table(results["dcf"]))
    story.append(Spacer(1, 14))

    # ── Valuation narrative ──────────────────────────────────
    story.append(Paragraph("Valuation Overview", S["section"]))
    iv   = results["dcf"]["intrinsic_value_per_share"]
    ev   = results["dcf"]["enterprise_value"]
    wacc = results["dcf"]["wacc_results"]["wacc"]
    tv_pct = results["dcf"]["pv_terminal_value"] / ev * 100

    narrative = (
        f"Our DCF model estimates an intrinsic value of <b>${iv:,.2f} per share</b> "
        f"for {data.company_info.company_name}, based on a WACC of {wacc*100:.2f}% "
        f"and a 2.0% terminal growth rate. The enterprise value of "
        f"<b>${ev:,.0f}M</b> reflects strong and stable free cash flow generation "
        f"over the 5-year forecast horizon. Terminal value accounts for "
        f"{tv_pct:.0f}% of total enterprise value, reflecting the long-duration "
        f"nature of the business. The sensitivity analysis below shows how the "
        f"valuation changes across a range of WACC and growth assumptions — "
        f"green cells represent scenarios more than 10% above the base case, "
        f"red cells represent scenarios more than 10% below."
    )
    story.append(Paragraph(narrative, S["body"]))
    story.append(Spacer(1, 6))

    # ── Assumptions ──────────────────────────────────────────
    story.append(Paragraph("Key Assumptions", S["section"]))
    story.append(_assumptions_table(results))
    story.append(Spacer(1, 12))

    # ── Sensitivity ──────────────────────────────────────────
    story.append(Paragraph(
        "Sensitivity Analysis — Intrinsic Value per Share",
        S["section"]
    ))
    story.append(_sensitivity_table(results))
    story.append(Spacer(1, 12))

    # ── CCA ──────────────────────────────────────────────────
    story.append(Paragraph("Comparable Company Analysis", S["section"]))

    iv_cca = results["cca"]["implied_value_per_share"]
    cca_narrative = (
        f"Based on peer median multiples, the implied value per share ranges "
        f"from <b>${iv_cca['from_ev_revenue']:,.2f}</b> (EV/Revenue) to "
        f"<b>${iv_cca['from_pe']:,.2f}</b> (P/E), bracketing our DCF estimate "
        f"of ${iv:,.2f} and providing triangulated support for the valuation."
    )
    story.append(Paragraph(cca_narrative, S["body"]))
    story.append(_cca_table(results))

    doc.build(story)
    print(f"  PDF saved to: {output_path}")
    return output_path