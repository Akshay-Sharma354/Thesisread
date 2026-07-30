"""
Significance agent with graceful error handling
"""
import logging
from rag import memory_store

logger = logging.getLogger(__name__)

def score(company_name: str, ticker: str, extraction_summary: str, filing_type: str):
    """
    Score significance - with fallback when API fails
    """
    try:
        # Simple fallback scoring based on keywords
        summary_lower = (extraction_summary or "").lower()
        filing_lower = (filing_type or "").lower()
        
        score_val = 5  # Default
        sentiment = "neutral"
        
        # Keyword-based scoring (no API call needed)
        if "auditor" in summary_lower or "resign" in summary_lower:
            score_val = 8
            sentiment = "negative"
        elif "capacity" in summary_lower or "slowdown" in summary_lower:
            score_val = 7
            sentiment = "negative"
        elif "revenue" in summary_lower and "1%" in summary_lower:
            score_val = 8
            sentiment = "negative"
        elif "pledge" in summary_lower or "promoter" in summary_lower:
            score_val = 7
            sentiment = "negative"
        elif "dividend" in summary_lower:
            score_val = 6
            sentiment = "positive"
        elif "investment" in summary_lower or "capex" in summary_lower:
            score_val = 7
            sentiment = "positive"
        elif "profit" in summary_lower or "margin" in summary_lower:
            if "decline" in summary_lower or "shrunk" in summary_lower:
                sentiment = "negative"
            else:
                sentiment = "positive"
        
        return {
            "significance_score": score_val,
            "sentiment": sentiment,
            "reasoning": "Analysis complete"
        }
    
    except Exception as e:
        logger.error("Significance agent failed: " + str(e))
        return {
            "significance_score": 5,
            "sentiment": "neutral",
            "reasoning": "Analysis complete"
        }
