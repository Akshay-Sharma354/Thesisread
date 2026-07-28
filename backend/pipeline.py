import uuid
from datetime import datetime, timezone

from agents import extraction_agent, significance_agent, comparator_agent, alert_agent
from rag import memory_store
from models import FilingInput

def run_pipeline(filing: FilingInput) -> dict:
    filing_id = str(uuid.uuid4())
    filed_at = filing.filed_at or datetime.now(timezone.utc).date().isoformat()

    # 1. Extraction
    extraction = extraction_agent.extract(filing.raw_text)
    extraction_dict = {
        "filing_type": extraction.filing_type,
        "key_entities": extraction.key_entities,
        "filing_date": extraction.filing_date,
        "regulation_reference": extraction.regulation_reference,
        "summary_plain_english": extraction.summary_plain_english,
    }

    # 2. Significance
    significance = significance_agent.score(
        company_name=filing.company_name,
        ticker=filing.ticker,
        extraction_summary=extraction.summary_plain_english,
        filing_type=extraction.filing_type,
    )
    significance_dict = {
        "significance_score": significance.significance_score,
        "sentiment": significance.sentiment,
        "reasoning": significance.reasoning,
        "risk_flags": significance.risk_flags,
        "opportunity_flags": significance.opportunity_flags,
    }

    # 3. Comparison
    comparison = comparator_agent.compare(
        ticker=filing.ticker,
        current_summary=extraction.summary_plain_english,
    )
    comparison_dict = {
        "has_history": comparison.has_history,
        "notable_changes": comparison.notable_changes,
        "pattern_note": comparison.pattern_note,
    }

    # 4. Alert composition
    alert = alert_agent.compose(
        company_name=filing.company_name,
        ticker=filing.ticker,
        summary=extraction.summary_plain_english,
        significance_reasoning=significance.reasoning,
        sentiment=significance.sentiment,
        pattern_note=comparison.pattern_note,
    )

    # 5. Persist to memory
    memory_store.add_filing(
        filing_id=filing_id,
        ticker=filing.ticker,
        company_name=filing.company_name,
        filing_type=extraction.filing_type,
        summary=extraction.summary_plain_english,
        significance_score=significance.significance_score,
        filed_at=filed_at,
    )

    return {
        "id": filing_id,
        "company_name": filing.company_name,
        "ticker": filing.ticker,
        "filed_at": filed_at,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "extraction": extraction_dict,
        "significance": significance_dict,
        "comparison": comparison_dict,
        "alert_headline": alert["alert_headline"],
        "alert_body": alert["alert_body"],
    }
