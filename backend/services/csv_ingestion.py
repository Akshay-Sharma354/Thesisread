"""
CSV filing uploader - user uploads CSV with filings, we process them.
"""
import logging
import csv
import io
from models import FilingInput
from pipeline import run_pipeline
from rag import memory_store

logger = logging.getLogger(__name__)

def ingest_from_csv(csv_content: str):
    """
    Process a CSV with columns: company_name, ticker, filing_text, filed_at
    """
    logger.info("Starting CSV filing ingestion...")
    
    try:
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)
        logger.info(f"Found {len(rows)} rows in CSV")
        
        processed_count = 0
        for row in rows:
            try:
                company_name = row.get('company_name', '').strip()
                ticker = row.get('ticker', '').strip()
                filing_text = row.get('filing_text', '').strip()
                filed_at = row.get('filed_at')
                
                if not all([company_name, ticker, filing_text]):
                    logger.warning(f"Skipping row - missing required fields")
                    continue
                
                if len(filing_text) < 50:
                    logger.warning(f"Skipping {company_name} - insufficient text")
                    continue
                
                # Check for duplicates
                existing = memory_store.all_recent(limit=1000)
                already_seen = any(
                    e.get('ticker') == ticker and filing_text[:100] in e.get('summary', '')
                    for e in existing
                )
                
                if already_seen:
                    logger.info(f"Skipping duplicate: {company_name}")
                    continue
                
                # Process through pipeline
                filing = FilingInput(
                    company_name=company_name,
                    ticker=ticker,
                    raw_text=filing_text,
                    filed_at=filed_at
                )
                
                analysis = run_pipeline(filing)
                processed_count += 1
                logger.info(f"✓ Processed {company_name} - Significance: {analysis['significance']['significance_score']}/10")
            
            except Exception as e:
                logger.error(f"Error processing row: {e}")
                continue
        
        logger.info(f"CSV ingestion complete: {processed_count} filings processed")
        return {"status": "success", "processed": processed_count, "total_rows": len(rows)}
    
    except Exception as e:
        logger.error(f"CSV parsing failed: {e}")
        raise
