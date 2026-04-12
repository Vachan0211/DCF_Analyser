from dataclasses import dataclass, field
from typing import List


@dataclass
class DCFAssumptions:
    # WACC inputs
    risk_free_rate: float = 0.0411      # 10-yr Treasury yield
    equity_risk_premium: float = 0.0446  # Damodaran ERP
    beta: float = 1.04                   # HD beta
    tax_rate: float = 0.24               # Effective tax rate

    # Revenue growth rates (5 years)
    revenue_growth_rates: List[float] = field(
        default_factory=lambda: [0.04, 0.04, 0.035, 0.03, 0.03]
    )

    # Margin assumptions
    gross_profit_margin: float = 0.334   # Gross profit / revenue
    sg_and_a_pct: float = 0.180          # SG&A / revenue
    capex_pct: float = 0.021             # Capex / revenue

    # DCF inputs
    terminal_growth_rate: float = 0.02   # Long-run perpetual growth
    projection_years: int = 5

    # Market data (for WACC weights)
    market_cap: float = 351973.0         # $ millions (shares * price)
    total_debt: float = 63754.0          # $ millions (ST + LT debt)

    def cost_of_equity(self) -> float:
        return self.risk_free_rate + self.beta * self.equity_risk_premium

    def after_tax_cost_of_debt(self, pre_tax_cost: float) -> float:
        return pre_tax_cost * (1 - self.tax_rate)