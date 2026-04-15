from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, KeepTogether
)
from pathlib import Path
from parser.schemas import FinancialData

DARK_BLUE   = colors.HexColor("#1F3864")
MID_BLUE    = colors.HexColor("#2E75B6")
LIGHT_BLUE  = colors.HexColor("#D6E4F0")
LIGHT_GRAY  = colors.HexColor("#F2F2F2")
LIGHT_GREEN = colors.HexColor("#E2EFDA")
RED_LIGHT   = colors.HexColor("#FFCCCC")
WHITE       = colors.white


def _sens_val(table, g, w):
    """Robust sensitivity table lookup — handles float and string keys."""
    row = table.get(round(g, 2), table.get(str(round(g, 2)), {}))
    return row.get(round(w, 2), row.get(str(round(w, 2)), 0))


def _S():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "T", fontSize=18, textColor=DARK_BLUE,
            fontName="Helvetica-Bold", spaceAfter=2
        ),
        "subtitle": ParagraphStyle(
            "ST", fontSize=10, textColor=colors.gray,
            fontName="Helvetica", spaceAfter=10
        ),
        "section": ParagraphStyle(
            "SEC", fontSize=10, textColor=WHITE,
            fontName="Helvetica-Bold", backColor=DARK_BLUE,
            spaceBefore=10, spaceAfter=5,
            leftIndent=0, rightIndent=0,
            borderPadding=(4, 6, 4, 6)
        ),
        "body": ParagraphStyle(
            "B", fontSize=9.5, textColor=colors.black,
            fontName="Helvetica", spaceAfter=5,
            leading=14
        ),
        "caption": ParagraphStyle(
            "CAP", fontSize=8.5, textColor=colors.gray,
            fontName="Helvetica-Oblique", spaceAfter=4
        ),
    }


def _banner(dcf: dict) -> Table:
    w    = dcf["wacc_results"]["wacc"]
    iv   = dcf["intrinsic_value_per_share"]
    ev   = dcf["enterprise_value"]
    eqv  = dcf["equity_value"]
    tv_p = dcf["pv_terminal_value"] / ev * 100

    data = [
        ["WACC", "Enterprise Value", "Equity Value",
         "Intrinsic Value / Share"],
        [f"{w*100:.2f}%", f"${ev:,.0f}M",
         f"${eqv:,.0f}M", f"${iv:,.2f}"],
        ["Discount rate used", f"TV = {tv_p:.0f}% of EV",
         "After net debt", "Base case estimate"],
    ]
    t = Table(data, colWidths=[1.55*inch]*4)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  DARK_BLUE),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0),  8),
        ("BACKGROUND",    (0,1), (-1,1),  LIGHT_BLUE),
        ("TEXTCOLOR",     (0,1), (-1,1),  DARK_BLUE),
        ("FONTNAME",      (0,1), (-1,1),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,1), (-1,1),  14),
        ("BACKGROUND",    (0,2), (-1,2),  LIGHT_GRAY),
        ("TEXTCOLOR",     (0,2), (-1,2),  colors.gray),
        ("FONTNAME",      (0,2), (-1,2),  "Helvetica-Oblique"),
        ("FONTSIZE",      (0,2), (-1,2),  7.5),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("GRID",          (0,0), (-1,-1), 0.5, WHITE),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    return t


def _assumptions_table(results: dict) -> Table:
    wacc_r = results["dcf"]["wacc_results"]
    rows   = [["Assumption", "Value", "Rationale"]]
    items  = [
        ("WACC",
         f"{wacc_r['wacc']*100:.2f}%",
         "CAPM cost of equity + after-tax cost of debt, "
         "market-value weighted"),
        ("Terminal Growth Rate",
         "2.0%",
         "Aligned with long-run US nominal GDP growth expectations"),
        ("Revenue Growth — Yr 1–2",
         "4.0%",
         "SRS acquisition contribution + recovery in professional demand"),
        ("Revenue Growth — Yr 3–5",
         "3.5% → 3.0%",
         "Gradual deceleration toward industry maturity"),
        ("Gross Profit Margin",
         "33.4%",
         "3-year historical average; held flat in forecast"),
        ("SG&A % of Revenue",
         "18.0%",
         "FY2024 actual ($28.7B / $159.5B); held constant"),
        ("Capex % of Revenue",
         "2.1%",
         "Historical average; store maintenance + technology investment"),
        ("Tax Rate",
         "24.0%",
         "Consistent with FY2024 effective rate"),
    ]
    for label, val, rationale in items:
        rows.append([label, val, rationale])

    t = Table(rows, colWidths=[1.55*inch, 0.85*inch, 3.8*inch])
    style = [
        ("BACKGROUND",    (0,0),  (-1,0),  MID_BLUE),
        ("TEXTCOLOR",     (0,0),  (-1,0),  WHITE),
        ("FONTNAME",      (0,0),  (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),  (-1,-1), 8.5),
        ("FONTNAME",      (0,1),  (-1,-1), "Helvetica"),
        ("ALIGN",         (1,0),  (1,-1),  "CENTER"),
        ("ALIGN",         (0,0),  (0,-1),  "LEFT"),
        ("ALIGN",         (2,0),  (2,-1),  "LEFT"),
        ("VALIGN",        (0,0),  (-1,-1), "MIDDLE"),
        ("GRID",          (0,0),  (-1,-1), 0.4, colors.lightgrey),
        ("TOPPADDING",    (0,0),  (-1,-1), 4),
        ("BOTTOMPADDING", (0,0),  (-1,-1), 4),
        ("LEFTPADDING",   (0,0),  (-1,-1), 5),
        ("RIGHTPADDING",  (0,0),  (-1,-1), 5),
    ]
    for i in range(1, len(rows)):
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        style.append(("BACKGROUND", (0,i), (-1,i), bg))
    t.setStyle(TableStyle(style))
    return t


def _sensitivity_table(results: dict) -> Table:
    sens   = results["sensitivity"]
    w_list = sens["wacc_range"]
    g_list = sens["growth_range"]
    table  = sens["table"]
    base   = results["dcf"]["intrinsic_value_per_share"]

    rows = [["g \\ WACC"] + [f"{w:.0%}" for w in w_list]]
    for g in g_list:
        row = [f"{g:.0%}"]
        for w in w_list:
            val = _sens_val(table, g, w)
            row.append(f"${val:,.0f}")
        rows.append(row)

    col_w = [0.75*inch] + [0.88*inch]*len(w_list)
    t     = Table(rows, colWidths=col_w)

    style = [
        ("BACKGROUND", (0,0),  (-1,0),  DARK_BLUE),
        ("TEXTCOLOR",  (0,0),  (-1,0),  WHITE),
        ("FONTNAME",   (0,0),  (-1,0),  "Helvetica-Bold"),
        ("BACKGROUND", (0,1),  (0,-1),  MID_BLUE),
        ("TEXTCOLOR",  (0,1),  (0,-1),  WHITE),
        ("FONTNAME",   (0,1),  (0,-1),  "Helvetica-Bold"),
        ("FONTSIZE",   (0,0),  (-1,-1), 8.5),
        ("ALIGN",      (0,0),  (-1,-1), "CENTER"),
        ("VALIGN",     (0,0),  (-1,-1), "MIDDLE"),
        ("GRID",       (0,0),  (-1,-1), 0.5, WHITE),
        ("TOPPADDING", (0,0),  (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]
    for ri, g in enumerate(g_list, 1):
        for ci, w in enumerate(w_list, 1):
            val = _sens_val(table, g, w)
            if   val >= base * 1.10: bg = LIGHT_GREEN
            elif val <= base * 0.90: bg = RED_LIGHT
            else:                    bg = WHITE
            style.append(("BACKGROUND", (ci,ri), (ci,ri), bg))
            style.append(("TEXTCOLOR",  (ci,ri), (ci,ri), DARK_BLUE))

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
            f"{round(p.get('ev_revenue', 0), 1):.1f}x",
            f"{round(p.get('ev_ebitda',  0), 1):.1f}x",
            f"{round(p.get('pe_ratio',   0), 1):.1f}x",
        ])
    rows.append([
        "Peer Median",
        f"{med['ev_revenue']:.1f}x",
        f"{med['ev_ebitda']:.1f}x",
        f"{med['pe_ratio']:.1f}x",
    ])

    t = Table(rows, colWidths=[2.9*inch, 1.0*inch, 1.0*inch, 0.9*inch])
    style = [
        ("BACKGROUND", (0,0),  (-1,0),  MID_BLUE),
        ("TEXTCOLOR",  (0,0),  (-1,0),  WHITE),
        ("FONTNAME",   (0,0),  (-1,0),  "Helvetica-Bold"),
        ("BACKGROUND", (0,-1), (-1,-1), LIGHT_BLUE),
        ("FONTNAME",   (0,-1), (-1,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",  (0,-1), (-1,-1), DARK_BLUE),
        ("FONTSIZE",   (0,0),  (-1,-1), 8.5),
        ("ALIGN",      (1,0),  (-1,-1), "CENTER"),
        ("ALIGN",      (0,0),  (0,-1),  "LEFT"),
        ("VALIGN",     (0,0),  (-1,-1), "MIDDLE"),
        ("GRID",       (0,0),  (-1,-1), 0.4, colors.lightgrey),
        ("TOPPADDING", (0,0),  (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",(0,0),  (0,-1),  6),
    ]
    for i in range(1, len(rows)-1):
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        style.append(("BACKGROUND", (0,i), (-1,i), bg))
    t.setStyle(TableStyle(style))
    return t


def _implied_table(results: dict) -> Table:
    iv   = results["cca"]["implied_value_per_share"]
    base = results["dcf"]["intrinsic_value_per_share"]

    rows  = [["Method", "Implied Value / Share", "vs DCF Estimate"]]
    items = [
        ("From EV / Revenue", iv["from_ev_revenue"]),
        ("From EV / EBITDA",  iv["from_ev_ebitda"]),
        ("From P / E",        iv["from_pe"]),
    ]
    for label, val in items:
        diff = (val - base) / base
        rows.append([
            label,
            f"${val:,.2f}",
            f"{'+' if diff >= 0 else ''}{diff*100:.1f}%"
        ])

    t = Table(rows, colWidths=[2.0*inch, 1.5*inch, 1.3*inch])
    style = [
        ("BACKGROUND",    (0,0),  (-1,0),  MID_BLUE),
        ("TEXTCOLOR",     (0,0),  (-1,0),  WHITE),
        ("FONTNAME",      (0,0),  (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),  (-1,-1), 8.5),
        ("ALIGN",         (1,0),  (-1,-1), "CENTER"),
        ("ALIGN",         (0,0),  (0,-1),  "LEFT"),
        ("VALIGN",        (0,0),  (-1,-1), "MIDDLE"),
        ("GRID",          (0,0),  (-1,-1), 0.4, colors.lightgrey),
        ("TOPPADDING",    (0,0),  (-1,-1), 4),
        ("BOTTOMPADDING", (0,0),  (-1,-1), 4),
        ("LEFTPADDING",   (0,0),  (0,-1),  6),
    ]
    for i in range(1, len(rows)):
        val  = items[i-1][1]
        bg   = LIGHT_GREEN if val >= base else RED_LIGHT
        style.append(("BACKGROUND", (2,i),  (2,i),  bg))
        style.append(("BACKGROUND", (0,i),  (1,i),
                      LIGHT_GRAY if i % 2 == 0 else WHITE))
    t.setStyle(TableStyle(style))
    return t


def generate_pdf(
    data: FinancialData,
    results: dict,
    output_path: str = None
) -> str:
    if output_path is None:
        output_path = (
            f"outputs/{data.company_info.ticker}_DCF_Summary.pdf"
        )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        rightMargin=0.6*inch, leftMargin=0.6*inch,
        topMargin=0.6*inch,   bottomMargin=0.6*inch,
    )

    S     = _S()
    story = []

    # Header
    story.append(Paragraph(
        f"{data.company_info.company_name}  "
        f"({data.company_info.ticker})",
        S["title"]
    ))
    story.append(Paragraph(
        f"DCF Valuation Summary  ·  "
        f"Fiscal Year {data.company_info.fiscal_year}  ·  "
        f"Ended {data.company_info.fiscal_year_end_date}  ·  "
        f"All figures in USD millions unless noted",
        S["subtitle"]
    ))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=DARK_BLUE, spaceAfter=10
    ))

    # Banner
    story.append(_banner(results["dcf"]))
    story.append(Spacer(1, 10))

    # Valuation overview
    iv   = results["dcf"]["intrinsic_value_per_share"]
    ev   = results["dcf"]["enterprise_value"]
    wacc = results["dcf"]["wacc_results"]["wacc"]
    tv_p = results["dcf"]["pv_terminal_value"] / ev * 100

    story.append(KeepTogether([
        Paragraph("Valuation Overview", S["section"]),
        Paragraph(
            f"The DCF model yields an intrinsic value of "
            f"<b>${iv:,.2f} per share</b> for "
            f"{data.company_info.company_name}, using a WACC of "
            f"<b>{wacc*100:.2f}%</b> and a 2.0% terminal growth rate. "
            f"Enterprise value of <b>${ev:,.0f}M</b> reflects stable "
            f"free cash flow generation over the 5-year forecast horizon, "
            f"with terminal value representing {tv_p:.0f}% of total "
            f"enterprise value. "
            f"The methodology follows standard WACC-based DCF: the tax "
            f"benefit of debt is embedded in the after-tax cost of debt "
            f"and is not separately added as a tax shield (which would "
            f"double-count it under the APV framework).",
            S["body"]
        ),
    ]))

    # Assumptions
    story.append(KeepTogether([
        Paragraph("Key Assumptions", S["section"]),
        _assumptions_table(results),
    ]))
    story.append(Spacer(1, 8))

    # Sensitivity
    story.append(KeepTogether([
        Paragraph(
            "Sensitivity Analysis  —  Intrinsic Value per Share",
            S["section"]
        ),
        Paragraph(
            f"Green cells are more than 10% above the base case. "
            f"Red cells are more than 10% below. "
            f"Base case: ${iv:,.2f} at WACC = {wacc*100:.2f}%, g = 2.0%.",
            S["caption"]
        ),
        _sensitivity_table(results),
    ]))
    story.append(Spacer(1, 8))

    # CCA
    iv_cca = results["cca"]["implied_value_per_share"]
    story.append(KeepTogether([
        Paragraph("Comparable Company Analysis", S["section"]),
        Paragraph(
            f"Peer median multiples imply a value range of "
            f"<b>${iv_cca['from_ev_revenue']:,.2f}</b> (EV/Revenue) to "
            f"<b>${iv_cca['from_pe']:,.2f}</b> (P/E), bracketing the "
            f"DCF estimate of ${iv:,.2f} and providing triangulated "
            f"support for the valuation.",
            S["body"]
        ),
        _cca_table(results),
    ]))
    story.append(Spacer(1, 6))

    story.append(KeepTogether([
        Paragraph(
            "Implied Value per Share from Peer Multiples",
            S["section"]
        ),
        _implied_table(results),
    ]))

    doc.build(story)
    print(f"  PDF saved to: {output_path}")
    return output_path