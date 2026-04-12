import yfinance as yf
from parser.schemas import FinancialData


def fetch_peer_data(ticker: str) -> dict:
    """Fetches market data for a peer company using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "ticker": ticker,
            "name": info.get("longName", ticker),
            "market_cap": info.get("marketCap", 0) / 1e6,
            "enterprise_value": info.get("enterpriseValue", 0) / 1e6,
            "revenue": info.get("totalRevenue", 0) / 1e6,
            "ebitda": info.get("ebitda", 0) / 1e6,
            "ebit": info.get("ebit", 0) / 1e6,
            "net_income": info.get("netIncomeToCommon", 0) / 1e6,
            "price": info.get("currentPrice", 0),
            "ev_revenue": info.get("enterpriseToRevenue", 0),
            "ev_ebitda": info.get("enterpriseToEbitda", 0),
            "pe_ratio": info.get("trailingPE", 0),
        }
    except Exception as e:
        print(f"Could not fetch data for {ticker}: {e}")
        return {"ticker": ticker, "error": str(e)}


def run_cca(
    data: FinancialData,
    peer_tickers: list = None
) -> dict:
    """
    Runs comparable company analysis against peer tickers.
    Computes EV/Revenue, EV/EBITDA, P/E for each peer
    and derives implied valuation for the subject company.
    """
    if peer_tickers is None:
        peer_tickers = ["LOW", "TSCO", "FND", "FERG"]

    print(f"Fetching peer data for: {peer_tickers}")
    peers = []
    for ticker in peer_tickers:
        peer = fetch_peer_data(ticker)
        if "error" not in peer:
            peers.append(peer)

    if not peers:
        return {"error": "Could not fetch any peer data"}

    # Median multiples
    ev_revenue_multiples = [
        p["ev_revenue"] for p in peers if p.get("ev_revenue", 0) > 0
    ]
    ev_ebitda_multiples = [
        p["ev_ebitda"] for p in peers if p.get("ev_ebitda", 0) > 0
    ]
    pe_multiples = [
        p["pe_ratio"] for p in peers if p.get("pe_ratio", 0) > 0
    ]

    def median(lst):
        if not lst:
            return 0
        s = sorted(lst)
        n = len(s)
        return s[n // 2] if n % 2 else (s[n//2 - 1] + s[n//2]) / 2

    median_ev_revenue = median(ev_revenue_multiples)
    median_ev_ebitda = median(ev_ebitda_multiples)
    median_pe = median(pe_multiples)

    # Subject company financials
    subject_revenue = data.income_statement.revenue
    subject_ebitda = (
        data.income_statement.operating_income +
        data.cash_flow_statement.depreciation_and_amortization
    )
    subject_net_income = data.income_statement.net_income
    shares = data.company_info.shares_outstanding
    net_debt = (
        data.balance_sheet.short_term_debt +
        data.balance_sheet.long_term_debt -
        data.balance_sheet.cash_and_equivalents
    )

    # Implied valuations
    def ev_to_equity_per_share(ev):
        return round((ev - net_debt) / shares, 2)

    implied_from_ev_revenue = ev_to_equity_per_share(
        median_ev_revenue * subject_revenue
    )
    implied_from_ev_ebitda = ev_to_equity_per_share(
        median_ev_ebitda * subject_ebitda
    )
    implied_from_pe = round(
        (median_pe * subject_net_income) / shares, 2
    )

    return {
        "peers": peers,
        "median_multiples": {
            "ev_revenue": round(median_ev_revenue, 2),
            "ev_ebitda": round(median_ev_ebitda, 2),
            "pe_ratio": round(median_pe, 2),
        },
        "implied_value_per_share": {
            "from_ev_revenue": implied_from_ev_revenue,
            "from_ev_ebitda": implied_from_ev_ebitda,
            "from_pe": implied_from_pe,
        },
    }