"""
Scheduled ingestion service - runs scraper, processes filings through pipeline.
"""
import logging
from scrapers.nse_scraper import fetch_nse_announcements, download_filing_text
from models import FilingInput
from pipeline import run_pipeline
from rag import memory_store

logger = logging.getLogger(__name__)

def ingest_nse_filings():
    """
    Fetch announcements from NSE, download full text, run through pipeline.
    Called by scheduler every N hours.
    """
    logger.info("Starting NSE filing ingestion...")
    
    announcements = fetch_nse_announcements()
    logger.info(f"Fetched {len(announcements)} announcements from NSE")
    
    processed_count = 0
    for ann in announcements:
        try:
            filing_text = download_filing_text(ann.get('filing_url'))
            
            if not filing_text or len(filing_text) < 50:
                logger.warning(f"Skipping {ann['company_name']} - insufficient text")
                continue
            
            existing = memory_store.all_recent(limit=1000)
            already_seen = any(
                e.get('ticker') == ann['ticker'] and ann['subject'] in e.get('summary', '')
                for e in existing
            )
            
            if already_seen:
                logger.info(f"Skipping duplicate: {ann['company_name']} - {ann['subject']}")
                continue
            
            filing = FilingInput(
                company_name=ann['company_name'],
                ticker=ann['ticker'],
                raw_text=filing_text,
                filed_at=ann.get('fetched_at')
            )
            
            analysis = run_pipeline(filing)
            processed_count += 1
            logger.info(f"✓ Processed {ann['company_name']} - Significance: {analysis['significance']['significance_score']}/10")
        
        except Exception as e:
            logger.error(f"Error processing {ann.get('company_name')}: {e}")
            continue
    
    logger.info(f"Ingestion complete: {processed_count} new filings processed")
    return {"status": "success", "processed": processed_count, "total_fetched": len(announcements)}
