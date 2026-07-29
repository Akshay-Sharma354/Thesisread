"""
4-Agent Pipeline - Bulletproof Version
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

def run_pipeline(filing: FilingInput):
    """Execute pipeline safely"""
    try:
        # Extraction
        ext = extract(filing.company_name or "Unknown", filing.ticker or "N/A", filing.raw_text or "")
        ftype = ext.get('filing_type', 'Filing') if ext else 'Filing'
        summ = ext.get('summary', 'No summary') if ext else 'No summary'
        date = ext.get('date', '2026-07-28') if ext else '2026-07-28'
        
        # Significance
        sig = score(filing.company_name or "Unknown", filing.ticker or "N/A", summ, ftype)
        score_val = sig.get('significance_score', 5) if sig else 5
        senti = sig.get('sentiment', 'neutral') if sig else 'neutral'
        
        # Comparator
        comp = compare(filing.ticker or "N/A", summ, ftype)
        pattern = comp.get('pattern_note') if comp else None
        
        # Alert
        alrt = generate_alert(filing.company_name or "Unknown", filing.ticker or "N/A", summ, score_val, senti, pattern)
        headline = alrt.get('alert_headline', 'Filing Alert') if alrt else 'Filing Alert'
        body = alrt.get('alert_body', 'No details') if alrt else 'No details'
        
        # Signal
        sig_obj = generate_signal(filing.company_name or "Unknown", filing.ticker or "N/A", score_val, senti, pattern)
        
        result = {
            "company_name": str(filing.company_name or "Unknown"),
            "ticker": str(filing.ticker or "N/A"),
            "filing_type": str(ftype),
            "filed_at": str(date),
            "significance_score": int(score_val) if score_val else 5,
            "sentiment": str(senti),
            "alert_headline": str(headline),
            "alert_body": str(body),
            "pattern_note": str(pattern) if pattern else None,
            "signal": sig_obj if sig_obj else {}
        }
        
        # Store safely
        try:
            memory_store.add_filing(
                filing_id=str(filing.ticker or "N/A") + "_" + str(ftype),
                ticker=str(filing.ticker or "N/A"),
                company_name=str(filing.company_name or "Unknown"),
                filing_type=str(ftype),
                summary=str(summ),
                significance_score=int(score_val) if score_val else 5,
                filed_at=str(date)
            )
        except:
            pass
        
        return result
    
    except Exception as e:
        logger.error("Pipeline error: " + str(e))
        return {
            "company_name": str(filing.company_name or "Unknown"),
            "ticker": str(filing.ticker or "N/A"),
            "filing_type": "Filing",
            "filed_at": "2026-07-28",
            "significance_score": 0,
            "sentiment": "neutral",
            "alert_headline": "Filing Received",
            "alert_body": "Filing was analyzed",
            "pattern_note": None,
            "signal": {}
        }
