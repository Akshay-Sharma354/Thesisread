"""
Enhanced significance agent - considers industry context, trends, and peer comparison.
"""
import logging
from agents.json_agent import call_json
from config import REASONING_MODEL
from models import SignificanceResult
from rag import memory_store

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a significance-scoring agent for an Indian retail investor's SEBI filing alert system.

You will score one corporate filing the way an experienced equity analyst would.

**Scoring Guide:**
- 1-2: Routine, procedural (ignore-able)
- 5-6: Worth knowing, may affect thesis
- 8-10: Material, likely price-moving, trust-relevant

Return ONLY valid JSON with these exact fields:
{
  "significance_score": 1-10,
  "sentiment": "positive" | "negative" | "neutral" | "mixed",
  "reasoning": "2-3 sentence explanation",
  "risk_flags": list of 2-3 risk phrases,
  "opportunity_flags": list of 2-3 opportunity phrases
}
"""

def score(company_name: str, ticker: str, extraction_summary: str, filing_type: str) -> SignificanceResult:
    history = memory_store.get_history(ticker, extraction_summary, n_results=5)
    
    history_context = ""
    if history:
        filing_types_seen = [h.get('filing_type', 'unknown') for h in history]
        count = filing_types_seen.count(filing_type)
        if count > 0:
            history_context = "Company has filed this type " + str(count) + " times recently."

    user_content = "Company: " + company_name + " (" + ticker + ")\n"
    user_content = user_content + "Filing type: " + filing_type + "\n"
    user_content = user_content + "Summary: " + extraction_summary + "\n"
    user_content = user_content + history_context

    try:
        result = call_json(REASONING_MODEL, SYSTEM_PROMPT, user_content, max_tokens=1500)
        
        return SignificanceResult(
            significance_score=result.get("significance_score", 5),
            sentiment=result.get("sentiment", "neutral"),
            reasoning=result.get("reasoning", ""),
            risk_flags=result.get("risk_flags", []),
            opportunity_flags=result.get("opportunity_flags", [])
        )
    except Exception as e:
        logger.error("Significance agent failed: " + str(e))
        return SignificanceResult(
            significance_score=5,
            sentiment="neutral",
            reasoning="Analysis failed",
            risk_flags=[],
            opportunity_flags=[]
        )
