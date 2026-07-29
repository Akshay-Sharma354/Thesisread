"""
CSV ingestion service - processes bulk filings
"""
import logging
import os
from io import StringIO
import csv
from pipeline import run_pipeline
from models import FilingInput
from services.email_service import send_filing_alert

logger = logging.getLogger(__name__)

def ingest_from_csv(csv_content: str):
    """Process filings from CSV"""
    try:
        reader = csv.DictReader(StringIO(csv_content))
        processed = 0
        failed = 0
        
        for row in reader:
            try:
                company_name = row.get('company_name', '').strip()
                ticker = row.get('ticker', '').strip()
                filing_text = row.get('filing_text', '').strip()
                
                if not all([company_name, ticker, filing_text]):
                    failed += 1
                    continue
                
                filing = FilingInput(company_name=company_name, ticker=ticker, raw_text=filing_text)
                result = run_pipeline(filing)
                
                significance_score = result.get('significance', {}).get('significance_score', 0)
                
                if significance_score >= 7:
                    alert_email = os.environ.get("ALERT_EMAIL")
                    if alert_email:
                        send_filing_alert(
                            recipient_email=alert_email,
                            company_name=company_name,
                            ticker=ticker,
                            headline=result.get('alert_headline', ''),
                            body=result.get('alert_body', ''),
                            significance_score=significance_score
                        )
                        logger.info("Email alert sent for " + company_name + " - Score: " + str(significance_score))
                
                processed += 1
                logger.info("✓ Processed " + company_name + " - Significance: " + str(significance_score) + "/10")
                
            except Exception as e:
                failed += 1
                logger.error("Failed to process row: " + str(e))
        
        return {
            "status": "success",
            "processed": processed,
            "failed": failed,
            "message": str(processed) + " filings processed, " + str(failed) + " failed"
        }
    
    except Exception as e:
        logger.error("CSV ingestion failed: " + str(e))
        return {"status": "error", "message": str(e)}
