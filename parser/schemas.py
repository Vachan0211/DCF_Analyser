from pydantic import BaseModel, Field
from typing import Optional


class IncomeStatement(BaseModel):
    revenue: float = Field(description="Total net revenue or net sales in millions")
    cost_of_sales: float = Field(description="Cost of goods sold / cost of sales in millions")
    gross_profit: float = Field(description="Gross profit in millions")
    sg_and_a: float = Field(description="Selling, general and administrative expenses in millions")
    depreciation_and_amortization: float = Field(description="D&A in millions")
    operating_income: float = Field(description="Operating income / EBIT in millions")
    interest_expense: float = Field(description="Interest expense in millions (positive number)")
    interest_income: float = Field(description="Interest income in millions")
    pre_tax_income: float = Field(description="Earnings before income tax in millions")
    tax_expense: float = Field(description="Income tax expense in millions")
    net_income: float = Field(description="Net earnings / net income in millions")


class BalanceSheet(BaseModel):
    cash_and_equivalents: float = Field(description="Cash and cash equivalents in millions")
    total_current_assets: float = Field(description="Total current assets in millions")
    total_assets: float = Field(description="Total assets in millions")
    total_current_liabilities: float = Field(description="Total current liabilities in millions")
    short_term_debt: float = Field(description="Short term debt / current portion of long term debt in millions")
    long_term_debt: float = Field(description="Long term debt in millions")
    total_liabilities: float = Field(description="Total liabilities in millions")
    total_equity: float = Field(description="Total stockholders equity in millions — can be negative")


class CashFlowStatement(BaseModel):
    operating_cash_flow: float = Field(description="Net cash from operating activities in millions")
    capital_expenditures: float = Field(description="Capital expenditures in millions (positive number)")
    depreciation_and_amortization: float = Field(description="D&A from cash flow statement in millions")


class CompanyInfo(BaseModel):
    company_name: str = Field(description="Full legal company name")
    ticker: str = Field(description="Stock ticker symbol")
    fiscal_year: int = Field(description="Fiscal year the statements cover e.g. 2024")
    fiscal_year_end_date: str = Field(description="Fiscal year end date e.g. February 2, 2025")
    shares_outstanding: float = Field(description="Diluted shares outstanding in millions")
    currency: str = Field(default="USD", description="Reporting currency")
    units: str = Field(default="millions", description="Units of financial figures")


class FinancialData(BaseModel):
    company_info: CompanyInfo
    income_statement: IncomeStatement
    balance_sheet: BalanceSheet
    cash_flow_statement: CashFlowStatement