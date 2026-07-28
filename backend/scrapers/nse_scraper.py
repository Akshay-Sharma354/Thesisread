"""
NSE corporate announcements scraper.
Pulls filings from https://www.nseindia.com/corporates/
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

NSE_ANNOUNCEMENTS_URL = "https://www.nseindia.com/corporates/"

def fetch_nse_announcements():
    """
    Fetch recent NSE corporate announcements.
    Returns list of (company_name, ticker, announcement_text, filing_url)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(NSE_ANNOUNCEMENTS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        announcements = []
        
        # Parse the announcements table
        rows = soup.find_all('tr')
        
        for row in rows[:20]:
            cells = row.find_all('td')
            if len(cells) < 4:
                continue
            
            try:
                company = cells[0].get_text(strip=True)
                ticker = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                subject = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                
                link = cells[-1].find('a')
                filing_url = link['href'] if link else None
                
                if company and ticker and subject:
                    announcements.append({
                        'company_name': company,
                        'ticker': ticker,
                        'subject': subject,
                        'filing_url': filing_url,
                        'fetched_at': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.warning(f"Error parsing announcement row: {e}")
                continue
        
        return announcements
    
    except requests.RequestException as e:
        logger.error(f"Failed to fetch NSE announcements: {e}")
        return []

def download_filing_text(filing_url: str) -> str:
    """
    Download the full text of a filing from its URL.
    Handles both PDF and HTML filings.
    """
    if not filing_url:
        return ""
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(filing_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        if filing_url.endswith('.pdf') or 'application/pdf' in response.headers.get('content-type', ''):
            from io import BytesIO
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(response.content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text.strip()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(separator='\n')
        return text.strip()
    
    except Exception as e:
        logger.error(f"Failed to download filing from {filing_url}: {e}")
        return ""
