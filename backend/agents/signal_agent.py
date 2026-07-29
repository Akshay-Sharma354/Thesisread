"""
Buy/Sell Signal Agent - generates investment signals
"""
import logging

logger = logging.getLogger(__name__)

def generate_signal(company_name: str, ticker: str, significance_score: int, sentiment: str, pattern_note: str = None):
    """
    Generate buy/sell signals
    """
    signal = None
    confidence = "LOW"
    reasoning = ""
    action = ""
    
    if significance_score >= 8 and sentiment == "negative":
        signal = "SELL"
        confidence = "HIGH"
        reasoning = "High-significance negative filing indicates material risk"
        action = "🔴 CONSIDER SELLING - Reduce position or avoid"
    
    elif significance_score >= 8 and sentiment == "positive":
        signal = "BUY"
        confidence = "HIGH"
        reasoning = "High-significance positive filing indicates growth opportunity"
        action = "🟢 CONSIDER BUYING - Look for entry points"
    
    elif significance_score >= 6 and sentiment == "negative":
        signal = "SELL"
        confidence = "MEDIUM"
        reasoning = "Material negative filing warrants caution"
        action = "🔴 CONSIDER SELLING - Monitor closely"
    
    elif significance_score >= 6 and sentiment == "positive":
        signal = "BUY"
        confidence = "MEDIUM"
        reasoning = "Material positive filing suggests opportunity"
        action = "🟢 CONSIDER BUYING - Consider accumulation"
    
    if pattern_note and ("anomaly" in pattern_note.lower() or "spike" in pattern_note.lower()):
        signal = "SELL"
        confidence = "MEDIUM"
        reasoning = "Pattern anomaly detected - " + pattern_note
        action = "🔴 CAUTION - Governance concern detected"
    
    return {
        "signal": signal,
        "confidence": confidence,
        "reasoning": reasoning,
        "action": action
    }
