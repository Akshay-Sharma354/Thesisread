from agents.json_agent import call_json
from config import REASONING_MODEL
from models import SignificanceResult

SYSTEM_PROMPT = """You are a significance-scoring agent for an Indian retail investor's SEBI filing
alert system. You will be given the extracted summary of one corporate filing.

Judge it the way an experienced equity analyst would when deciding whether a retail investor
watching this stock should be alerted:

- significance_score: integer 1-10. 1-2 = routine/procedural (ignore-able), 5-6 = worth knowing,
  8-10 = material and likely price-moving or trust-relevant (e.g. auditor resignation, promoter
  pledge spike, related-party deal favoring promoters, sharp guidance cut, regulatory action).
- sentiment: "positive", "negative", "neutral", or "mixed" from a shareholder's perspective.
- reasoning: 1-2 sentences on WHY it matters (or doesn't) - not just what happened.
- risk_flags: short phrases for any governance/financial/operational red flags (empty list if none).
- opportunity_flags: short phrases for anything positive for shareholders (empty list if none).

Be conservative with high scores - most routine filings (address changes, standard compliance
certificates, routine board meeting intimations) should score 1-3. Reserve 7+ for things that
would actually change how someone thinks about the stock.

Return exactly these fields as JSON: significance_score, sentiment, reasoning, risk_flags, opportunity_flags.
"""


def score(company_name: str, ticker: str, extraction_summary: str, filing_type: str) -> SignificanceResult:
    user_content = (
        f"Company: {company_name} ({ticker})\n"
        f"Filing type: {filing_type}\n"
        f"Extracted summary: {extraction_summary}"
    )
    result = call_json(REASONING_MODEL, SYSTEM_PROMPT, user_content)
    return SignificanceResult(**result)
