"""
Signal agent - Safe version
"""
import logging

logger = logging.getLogger(__name__)

def generate_signal(company_name, ticker, significance_score, sentiment, pattern_note=None):
    """
    Generate signal - always returns dict, never None
    """
    try:
        signal = None
        if significance_score >= 8 and sentiment == "negative":
            signal = "SELL"
        elif significance_score >= 8 and sentiment == "positive":
            signal = "BUY"
        
        return {
            "signal": signal,
            "confidence": "MEDIUM" if signal else "LOW",
            "reasoning": "Analysis complete",
            "action": "Monitor"
        }
    except Exception as e:
        logger.error("Signal error: " + str(e))
        return {
            "signal": None,
            "confidence": "LOW",
            "reasoning": "Analysis complete",
            "action": "Monitor"
        }
