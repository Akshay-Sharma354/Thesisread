"""
Alert Agent - generates final alert headlines and bodies
"""
import logging

logger = logging.getLogger(__name__)

def generate_alert(company_name: str, ticker: str, extraction_summary: str, significance_score: int, sentiment: str, pattern_note: str = None):
    """
    Generate alert headline and body
    """
    
    if significance_score >= 8:
        if sentiment == "negative":
            headline = company_name + " - Critical Negative Filing"
        elif sentiment == "positive":
            headline = company_name + " - Major Positive Development"
        else:
            headline = company_name + " - Material Filing"
    else:
        headline = company_name + " - " + ticker + " Filing Update"
    
    body = extraction_summary[:300] if extraction_summary else "Filing analysis completed"
    if extraction_summary and len(extraction_summary) > 300:
        body = body + "..."
    
    return {
        "alert_headline": headline,
        "alert_body": body
    }
