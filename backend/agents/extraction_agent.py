from agents.json_agent import call_json
from config import FAST_MODEL
from models import ExtractionResult

SYSTEM_PROMPT = """You are a SEBI regulatory filing extraction agent for the Indian stock market.

Given the raw text of a corporate filing (from NSE/BSE/SEBI disclosures), extract:
- filing_type: one short category, e.g. "Financial Results", "Board Meeting Outcome",
  "Resignation/Appointment", "Related Party Transaction", "Promoter Shareholding/Pledge",
  "Auditor Change", "Corporate Action", "Regulatory Order", "Other"
- key_entities: important named people, subsidiaries, amounts, or dates mentioned (list of short strings)
- filing_date: the date the filing was made or the event occurred, in YYYY-MM-DD format if determinable, else null
- regulation_reference: the specific SEBI/LODR regulation cited, if any (e.g. "Regulation 30, SEBI LODR"), else null
- summary_plain_english: 2-3 sentences explaining what this filing says, in plain English a
  non-finance retail investor would understand. No jargon.

Return exactly these fields as JSON: filing_type, key_entities, filing_date, regulation_reference, summary_plain_english.
"""


def extract(raw_text: str) -> ExtractionResult:
    result = call_json(FAST_MODEL, SYSTEM_PROMPT, raw_text)
    return ExtractionResult(**result)
