"""
Enhanced comparator agent - detects patterns, anomalies, and behavioral trends.
"""
import logging
from agents.json_agent import call_json
from config import REASONING_MODEL
from models import ComparisonResult
from rag import memory_store

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an advanced pattern-detection agent for an Indian stock market filing analyzer.

You are given ONE new filing for a company, plus that company's past filing summaries (most relevant first).

Your job: Spot PATTERNS and ANOMALIES that humans skimming filings would miss.

**Patterns to look for:**
- Recurring events at increasing frequency (auditor changes, related-party deals, management resignations)
- Behavioral trends (promoter pledging every 6 months, always during stock rallies)
- Contradictions (promised capex that never materialized, guidance that keeps getting cut)
- Sudden deviations from historical baseline

**Anomalies to flag:**
- "Sudden spike in related-party transactions after 2 years of silence"
- "This is the 4th management resignation in 12 months (vs 1 in prior 5 years)"
- "Company now pledging 40% of promoter stake vs historical 5-10%"
- "Auditor resignation 14 months in (vs historical 4.8 year average tenure)"

Return ONLY valid JSON with these exact fields:
{
  "has_history": boolean,
  "notable_changes": list of 2-3 specific changes compared to history (empty if none),
  "pattern": one sentence describing a multi-filing pattern, or null if none detected,
  "anomaly": one sentence flagging a deviation from historical norm, or null if none,
  "frequency_trend": "accelerating" or "stable" or "decelerating" or null
}
"""

def compare(ticker: str, current_summary: str, filing_type: str = None):
    """
    Compare current filing against history. Detect patterns AND anomalies.
    """
    history = memory_store.get_history(ticker, current_summary, n_results=10)

    if not history:
        return ComparisonResult(has_history=False, notable_changes=[], pattern_note=None)

    history_text = "\n".join(
        "- [" + h.get('filed_at', 'unknown date') + "] (" + h.get('filing_type', 'unknown') + ") " + h['summary']
        for h in history
    )

    user_content = "Company: " + ticker + "\n"
    user_content = user_content + "Current filing type: " + str(filing_type) + "\n"
    user_content = user_content + "Current summary: " + current_summary + "\n\n"
    user_content = user_content + "Past 10 filings (most similar first):\n" + history_text + "\n\n"
    user_content = user_content + "Analyze for patterns and anomalies."

    try:
        result = call_json(REASONING_MODEL, SYSTEM_PROMPT, user_content, max_tokens=1500)
        
        pattern_note = None
        if result.get("pattern"):
            pattern_note = result["pattern"]
        if result.get("anomaly"):
            if pattern_note:
                pattern_note = result["anomaly"] + " " + pattern_note
            else:
                pattern_note = result["anomaly"]
        
        return ComparisonResult(
            has_history=result.get("has_history", True),
            notable_changes=result.get("notable_changes", []),
            pattern_note=pattern_note
        )
    except Exception as e:
        logger.error("Comparator agent failed: " + str(e))
        return ComparisonResult(has_history=len(history) > 0, notable_changes=[], pattern_note=None)
