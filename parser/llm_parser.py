import os
import json
import anthropic
from dotenv import load_dotenv
from parser.schemas import FinancialData

load_dotenv()


SYSTEM_PROMPT = """You are a financial analyst extracting data from a 10-K annual report.
Extract financial data for the MOST RECENT fiscal year only.

Rules:
- All dollar figures must be in MILLIONS (if the filing reports in thousands, divide by 1000)
- If a value is shown in parentheses it means negative — but report interest expense and capex as positive numbers
- If you cannot find a value with confidence, use 0.0
- Do not guess or estimate — only extract what is explicitly stated
- Return ONLY valid JSON, no explanation or markdown

Return this exact JSON structure:
{
  "company_info": {
    "company_name": "",
    "ticker": "",
    "fiscal_year": 0,
    "fiscal_year_end_date": "",
    "shares_outstanding": 0.0,
    "currency": "USD",
    "units": "millions"
  },
  "income_statement": {
    "revenue": 0.0,
    "cost_of_sales": 0.0,
    "gross_profit": 0.0,
    "sg_and_a": 0.0,
    "depreciation_and_amortization": 0.0,
    "operating_income": 0.0,
    "interest_expense": 0.0,
    "interest_income": 0.0,
    "pre_tax_income": 0.0,
    "tax_expense": 0.0,
    "net_income": 0.0
  },
  "balance_sheet": {
    "cash_and_equivalents": 0.0,
    "total_current_assets": 0.0,
    "total_assets": 0.0,
    "total_current_liabilities": 0.0,
    "short_term_debt": 0.0,
    "long_term_debt": 0.0,
    "total_liabilities": 0.0,
    "total_equity": 0.0
  },
  "cash_flow_statement": {
    "operating_cash_flow": 0.0,
    "capital_expenditures": 0.0,
    "depreciation_and_amortization": 0.0
  }
}"""


def parse_financials_with_llm(extracted_text: str) -> FinancialData:
    """
    Sends extracted 10-K text to Claude with prompt caching enabled.
    The large document content is cached for 5 minutes — repeated runs
    on the same 10-K cost ~10% of the normal input price.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in .env file")

    client = anthropic.Anthropic(api_key=api_key)

    print("Sending to Claude with prompt caching enabled...")

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract the financial data from this 10-K filing:\n\n" + extracted_text,
                        "cache_control": {"type": "ephemeral"}
                    }
                ]
            }
        ],
        extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
    )

    # Show cache usage so you can see the savings
    usage = message.usage
    print(f"Tokens used:")
    print(f"  Input:          {usage.input_tokens:,}")
    print(f"  Cache written:  {getattr(usage, 'cache_creation_input_tokens', 0):,}")
    print(f"  Cache read:     {getattr(usage, 'cache_read_input_tokens', 0):,}")
    print(f"  Output:         {usage.output_tokens:,}")

    cache_read = getattr(usage, 'cache_read_input_tokens', 0)
    if cache_read > 0:
        print(f"  Cache HIT — saved ~90% on {cache_read:,} tokens")
    else:
        print(f"  Cache MISS — document cached for next 5 minutes")

    raw_response = message.content[0].text

    try:
        raw_response = raw_response.strip()
        if raw_response.startswith("```"):
            raw_response = raw_response.split("```")[1]
            if raw_response.startswith("json"):
                raw_response = raw_response[4:]

        data_dict = json.loads(raw_response)

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response:\n{raw_response}")
        raise ValueError("Claude did not return valid JSON.")

    financial_data = FinancialData(**data_dict)
    print("Data validated successfully.")

    return financial_data