import json
import os
from typing import List, Dict
from datetime import datetime, timezone

STORAGE_PATH = os.path.join(os.path.dirname(__file__), "filings.json")

def _load():
    if os.path.exists(STORAGE_PATH):
        with open(STORAGE_PATH, "r") as f:
            return json.load(f)
    return []

def _save(data):
    with open(STORAGE_PATH, "w") as f:
        json.dump(data, f, indent=2)

def add_filing(filing_id: str, ticker: str, company_name: str, filing_type: str,
                summary: str, significance_score: int, filed_at: str) -> None:
    data = _load()
    data.append({
        "id": filing_id,
        "ticker": ticker,
        "company_name": company_name,
        "filing_type": filing_type,
        "summary": summary,
        "significance_score": significance_score,
        "filed_at": filed_at,
        "stored_at": datetime.now(timezone.utc).isoformat(),
    })
    _save(data)

def get_history(ticker: str, current_summary: str, n_results: int = 5) -> List[Dict]:
    data = _load()
    ticker_filings = [r for r in data if r.get("ticker", "").upper() == ticker.upper()]
    return ticker_filings[-n_results:] if ticker_filings else []

def all_recent(limit: int = 50) -> List[Dict]:
    data = _load()
    data.sort(key=lambda r: r.get("stored_at", ""), reverse=True)
    return data[:limit]
