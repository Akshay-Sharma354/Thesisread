"""
Enhanced comparator agent - detects patterns, anomalies, and behavioral trends.
"""
import logging
from agents.json_agent import call_json
from config import REASONING_MODEL
from rag import memory_store

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a pattern-detection agent.

Given a filing and past filings for the same company, detect patterns and anomalies.

Return ONLY valid JSON:
{
  "has_history": boolean,
  "pattern": "one sentence describing a multi-filing pattern, or null",
  "anomaly": "one sentence flagging a deviation, or null"
}
"""

def compare(ticker: str, current_summary: str, filing_type: str = None):
    """
    Compare current filing against history. Detect patterns AND anomalies.
    """
    history = memory_store.get_history(ticker, current_summary, n_results=10)

    if not history:
        return {
            "has_history": False,
            "notable_changes": [],
            "pattern_note": None
        }

    history_text = "\n".join(
        "- [" + h.get('filed_at', 'unknown date') + "] (" + h.get('filing_type', 'unknown') + ") " + h['summary']
        for h in history
    )

    user_content = "Company: " + ticker + "\n"
    user_content = user_content + "Current filing type: " + str(filing_type) + "\n"
    user_content = user_content + "Current summary: " + current_summary + "\n\n"
    user_content = user_content + "Past 10 filings:\n" + history_text + "\n\n"
    user_content = user_content + "Analyze for patterns and anomalies."

    try:
        result = call_json(REASONING_MODEL, SYSTEM_PROMPT, user_content, max_tokens=500)
        
        pattern_note = None
        if result.get("pattern"):
            pattern_note = result["pattern"]
        if result.get("anomaly"):
            if pattern_note:
                pattern_note = result["anomaly"] + " " + pattern_note
            else:
                pattern_note = result["anomaly"]
        
        return {
            "has_history": result.get("has_history", True),
            "notable_changes": result.get("notable_changes", []),
            "pattern_note": pattern_note
        }
    except Exception as e:
        logger.error("Comparator agent failed: " + str(e))
        return {
            "has_history": len(history) > 0,
            "notable_changes": [],
            "pattern_note": None
        }
