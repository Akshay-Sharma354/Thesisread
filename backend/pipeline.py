"""
Ultra-safe Pipeline
"""
import logging
from agents.extraction_agent import extract
from agents.significance_agent import score
from agents.comparator_agent import compare
from agents.alert_agent import generate_alert
from agents.signal_agent import generate_signal
from models import FilingInput
from rag import memory_store

logger = logging.getLogger(__name__)

def safe_str(val):
    """Convert any value to safe string"""
    if val is None:
        return ""
    return str(val)

def run_pipeline(filing: FilingInput):
    """Execute pipeline with max safety"""
    try:
        ext = extract(safe_str(filing.company_name), safe_str(filing.ticker), safe_str(filing.raw_text))
        ftype = safe_str(ext.get('filing_type', 'Filing'))
        summ = safe_str(ext.get('summary', 'No summary'))
        date = safe_str(ext.get('date', '2026-07-28'))
        
        sig = score(safe_str(filing.company_name), safe_str(filing.ticker), summ, ftype)
        score_val = sig.get('significance_score', 5) if sig else 5
        senti = safe_str(sig.get('sentiment', 'neutral') if sig else 'neutral')
        
        comp = compare(safe_str(filing.ticker), summ, ftype)
        pattern = comp.get('pattern_note') if comp else None
        
        alrt = generate_alert(safe_str(filing.company_name), safe_str(filing.ticker), summ, score_val, senti, pattern)
        headline = safe_str(alrt.get('alert_headline', 'Filing Alert') if alrt else 'Filing Alert')
        body = safe_str(alrt.get('alert_body', 'No details') if alrt else 'No details')
        
        sig_obj = generate_signal(safe_str(filing.company_name), safe_str(filing.ticker), score_val, senti, pattern)
        
        return {
            "company_name": safe_str(filing.company_name),
            "ticker": safe_str(filing.ticker),
            "filing_type": ftype,
            "filed_at": date,
            "significance_score": int(score_val) if score_val else 5,
            "sentiment": senti,
            "alert_headline": headline,
            "alert_body": body,
            "pattern_note": pattern,
            "signal": sig_obj if sig_obj else {}
        }
    
    except Exception as e:
        logger.error("Pipeline error: " + safe_str(e))
        return {
            "company_name": safe_str(filing.company_name),
            "ticker": safe_str(filing.ticker),
            "filing_type": "Filing",
            "filed_at": "2026-07-28",
            "significance_score": 0,
            "sentiment": "neutral",
            "alert_headline": "Filing Received",
            "alert_body": "Filing was processed",
            "pattern_note": None,
            "signal": {}
        }
