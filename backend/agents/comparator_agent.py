from agents.json_agent import call_json
from config import REASONING_MODEL
from models import ComparisonResult
from rag import memory_store

SYSTEM_PROMPT = """You are a pattern-detection agent. You are given one new filing summary for a
company, plus a list of that company's past filing summaries (most relevant first).

Your job: spot what's DIFFERENT or REPEATING compared to history that a human skimming
each filing individually would miss. Examples of what to look for:
- A number that changed direction (margins improving -> declining, debt going up)
- A repeated event (e.g. this is the Nth auditor/CFO change, Nth related-party deal)
- A contradiction between what was said before and what's being said now
- A pattern only visible across multiple filings (e.g. promoter pledge creeping up filing after filing)

If there is no meaningful history, or nothing notable emerges from comparison, say so plainly -
do not invent patterns.

Return exactly these fields as JSON:
- has_history: boolean, whether any past filings were available to compare against
- notable_changes: list of short strings describing specific changes/differences found (empty if none)
- pattern_note: one sentence flagging a recurring pattern across 2+ filings, or null if none
"""


def compare(ticker: str, current_summary: str) -> ComparisonResult:
    history = memory_store.get_history(ticker, current_summary)

    if not history:
        return ComparisonResult(has_history=False, notable_changes=[], pattern_note=None)

    history_text = "\n".join(
        f"- [{h.get('filed_at', 'unknown date')}] ({h.get('filing_type', 'unknown type')}) {h['summary']}"
        for h in history
    )
    user_content = f"New filing summary:\n{current_summary}\n\nPast filings for this company:\n{history_text}"

    result = call_json(REASONING_MODEL, SYSTEM_PROMPT, user_content)
    return ComparisonResult(**result)
