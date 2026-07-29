"""
Helper functions to detect statistical anomalies in filing patterns.
"""
from datetime import datetime, timedelta
from typing import List, Dict

def detect_frequency_spike(ticker: str, filing_type: str, history: 
List[Dict], threshold_days: int = 180) -> bool:
    """
    Detect if a filing type is happening much faster than historical 
baseline.
    E.g., if auditor changes usually happen every 4 years but now 3x in 18 
months.
    """
    if len(history) < 2:
        return False
    
    # Find past filings of same type
    same_type = [h for h in history if h.get('filing_type') == 
filing_type]
    
    if len(same_type) < 2:
        return False
    
    # Calculate average gap between filings
    dates = []
    for h in same_type:
        try:
            date = datetime.fromisoformat(h.get('filed_at', ''))
            dates.append(date)
        except:
            continue
    
    if len(dates) < 2:
        return False
    
    dates.sort()
    gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
    avg_gap = sum(gaps) / len(gaps)
    recent_gap = (datetime.now() - dates[-1]).days
    
    # If recent gap is 50% shorter than average, it's a spike
    return recent_gap < (avg_gap * 0.5)

def detect_volume_anomaly(ticker: str, filing_type: str, history: 
List[Dict], window_days: int = 365) -> bool:
    """
    Detect if we're seeing abnormally high volume of a filing type.
    E.g., 3 related-party deals in 6 months vs 1 every 18 months 
historically.
    """
    if len(history) < 3:
        return False
    
    same_type = [h for h in history if h.get('filing_type') == 
filing_type]
    
    if len(same_type) < 2:
        return False
    
    # Count filings in last window_days
    recent_count = 0
    for h in same_type:
        try:
            date = datetime.fromisoformat(h.get('filed_at', ''))
            if (datetime.now() - date).days < window_days:
                recent_count += 1
        except:
            continue
    
    # If more than 2 filings in window_days, it's anomalous
    return recent_count >= 3

def get_anomaly_description(ticker: str, filing_type: str, history: 
List[Dict]) -> str:
    """
    Return a human-readable description of detected anomalies.
    """
    if detect_frequency_spike(ticker, filing_type, history):
        return f"Filing frequency spike: {filing_type}s happening 2x 
faster than historical baseline"
    
    if detect_volume_anomaly(ticker, filing_type, history):
        return f"Volume anomaly: Multiple {filing_type}s in short time 
window (unusual pattern)"
    
    return None
