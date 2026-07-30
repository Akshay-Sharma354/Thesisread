"""
Alert Agent - With detailed logging
"""
import logging

logger = logging.getLogger(__name__)

def generate_alert(company_name, ticker, extraction_summary, significance_score, sentiment, pattern_note=None):
    """Generate specific headlines"""
    
    try:
        company = str(company_name) if company_name else "Unknown"
        summary = str(extraction_summary) if extraction_summary else ""
        
        logger.info("ALERT_AGENT: Company=" + company + " Summary length=" + str(len(summary)))
        
        summary_lower = summary.lower()
        
        # Detect filing type from summary
        headline = company + " - Filing"
        
        if "capacity" in summary_lower:
            headline = company + " - Production Slowdown"
            logger.info("DETECTED: Capacity issue")
        elif "revenue" in summary_lower:
            headline = company + " - Revenue Alert"
            logger.info("DETECTED: Revenue issue")
        elif "auditor" in summary_lower:
            headline = company + " - Auditor Change"
            logger.info("DETECTED: Auditor change")
        elif "resign" in summary_lower:
            headline = company + " - Executive Resignation"
            logger.info("DETECTED: Resignation")
        elif "pledge" in summary_lower:
            headline = company + " - Promoter Alert"
            logger.info("DETECTED: Pledge")
        elif "dividend" in summary_lower:
            headline = company + " - Dividend News"
            logger.info("DETECTED: Dividend")
        
        body = summary[:400] if len(summary) > 400 else summary
        
        logger.info("ALERT_AGENT: Generated headline=" + headline)
        
        return {
            "alert_headline": headline,
            "alert_body": body
        }
    
    except Exception as e:
        logger.error("Alert agent error: " + str(e))
        return {
            "alert_headline": "Filing Alert",
            "alert_body": "Filing processed"
        }
