from agents.json_agent import call_json
from config import FAST_MODEL

SYSTEM_PROMPT = """You write the final alert a retail investor sees in their feed for one filing.
Given the filing summary, significance score/reasoning, and any historical pattern notes, write:

- alert_headline: one short punchy line (under 12 words), plain English, no jargon, no hype.
  E.g. "Sun Pharma flags 3rd related-party deal this year" not "Material Event Disclosure Filed".
- alert_body: 2-4 sentences. State what happened, why it matters, and (if a pattern_note exists)
  connect it to the pattern. Neutral, factual tone - explain, don't hype and don't editorialize
  with investment advice like "buy" or "sell".

Return exactly these fields as JSON: alert_headline, alert_body.
"""


def compose(company_name: str, ticker: str, summary: str, significance_reasoning: str,
            sentiment: str, pattern_note: str | None) -> dict:
    user_content = (
        f"Company: {company_name} ({ticker})\n"
        f"Filing summary: {summary}\n"
        f"Why it matters: {significance_reasoning}\n"
        f"Sentiment: {sentiment}\n"
        f"Pattern note: {pattern_note or 'none'}"
    )
    return call_json(FAST_MODEL, SYSTEM_PROMPT, user_content)
