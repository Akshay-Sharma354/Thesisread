"""
Extraction Agent - extracts key information from filings
"""
import logging

logger = logging.getLogger(__name__)

def extract(company_name: str, ticker: str, raw_text: str):
    """
    Extract key information from filing text - simplified version
    """
    
    # Simple extraction without Claude
    filing_type = "Filing"
    
    # Detect filing type from text
    text_lower = raw_text.lower()
    if "auditor" in text_lower:
        filing_type = "Auditor Change"
    elif "related party" in text_lower or "rpt" in text_lower:
        filing_type = "Related Party Transaction"
    elif "dividend" in text_lower:
        filing_type = "Dividend"
    elif "financial results" in text_lower or "revenue" in text_lower:
        filing_type = "Financial Results"
    elif "resignation" in text_lower:
        filing_type = "Management Change"
    elif "acquisition" in text_lower or "merger" in text_lower:
        filing_type = "M&A"
    
    # Get summary from first 300 chars
    summary = raw_text[:300].strip()
    if len(raw_text) > 300:
        summary = summary + "..."
    
    return {
        "filing_type": filing_type,
        "summary": summary,
        "key_entities": [company_name, ticker],
        "date": "2026-07-28"
    }
