from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class ExtractionResult:
    filing_type: str
    key_entities: List[str] = field(default_factory=list)
    filing_date: Optional[str] = None
    regulation_reference: Optional[str] = None
    summary_plain_english: str = ""

@dataclass
class SignificanceResult:
    significance_score: int
    sentiment: str
    reasoning: str
    risk_flags: List[str] = field(default_factory=list)
    opportunity_flags: List[str] = field(default_factory=list)

@dataclass
class ComparisonResult:
    has_history: bool
    notable_changes: List[str] = field(default_factory=list)
    pattern_note: Optional[str] = None

@dataclass
class FilingInput:
    company_name: str
    ticker: str
    raw_text: str
    filed_at: Optional[str] = None

@dataclass
class FilingAnalysis:
    id: str
    company_name: str
    ticker: str
    filed_at: str
    analyzed_at: str
    extraction: dict
    significance: dict
    comparison: dict
    alert_headline: str
    alert_body: str
