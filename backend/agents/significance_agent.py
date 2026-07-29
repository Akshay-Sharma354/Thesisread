"""
Enhanced significance agent - considers industry context, trends, and peer comparison.
"""
import logging
from agents.json_agent import call_json
from config import REASONING_MODEL
from rag import memory_store

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a significance-scoring agent for retail investors.

Score 1-10 based on how much this filing matters to shareholders:
- 1-2: Routine (ignore)
- 5-6: Worth knowing
- 8-10: Material, price-moving

Return ONLY valid JSON:
{
  "significance_score": 1-10,
  "sentiment": "positive" | "negative" | "neutral" | "mixed",
  "reasoning": "2-3 sentence explanation"
}
"""

def score(company_name: str, ticker: str, extraction_summary: str, filing_type: str):
    """
    Score significance with context
    """
    history = memory_store.get_history(ticker, extraction_summary, n_results=5)
    
    history_context = ""
    if history:
        filing_types_seen = [h.get('filing_type', 'unknown') for h in history]
        count = filing_types_seen.count(filing_type)
        if count > 0:
            history_context = " Company has filed this type " + str(count) + " times recently."

    user_content = "Company: " + company_name + " (" + ticker + ")\n"
    user_content = user_content + "Filing type: " + filing_type + "\n"
    user_content = user_content + "Summary: " + extraction_summary + "\n"
    user_content = user_content + history_context

    try:
        result = call_json(REASONING_MODEL, SYSTEM_PROMPT, user_content, max_tokens=500)
        
        return {
            "significance_score": result.get("significance_score", 5),
            "sentiment": result.get("sentiment", "neutral"),
            "reasoning": result.get("reasoning", "")
        }
    except Exception as e:
        logger.error("Significance agent failed: " + str(e))
        return {
            "significance_score": 5,
            "sentiment": "neutral",
            "reasoning": "Analysis failed"
        }
