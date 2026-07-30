"""
Comparator - Safe fallback version
"""
import logging

logger = logging.getLogger(__name__)

def compare(ticker: str, current_summary: str, filing_type: str = None):
    """
    Compare - always returns a dict, never None
    """
    try:
        return {
            "has_history": False,
            "notable_changes": [],
            "pattern_note": None
        }
    except Exception as e:
        logger.error("Comparator error: " + str(e))
        return {
            "has_history": False,
            "notable_changes": [],
            "pattern_note": None
        }
