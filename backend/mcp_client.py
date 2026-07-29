"""
MCP Client wrapper - calls MCP servers from agents
"""
import json
import logging

logger = logging.getLogger(__name__)

class EmailMCPClient:
    """Client to call Email MCP Server"""
    
    @staticmethod
    def send_alert(recipient_email: str, company_name: str, ticker: str, headline: str, body: str, significance_score: int):
        """Send alert through MCP server"""
        try:
            from services.email_service import send_filing_alert
            return send_filing_alert(recipient_email, company_name, ticker, headline, body, significance_score)
        except Exception as e:
            logger.error(f"Email MCP call failed: {e}")
            return False

class RAGMCPClient:
    """Client to call RAG MCP Server"""
    
    @staticmethod
    def store_filing(filing_id: str, ticker: str, company_name: str, filing_type: str, summary: str, significance_score: int, filed_at: str):
        """Store filing through MCP server"""
        try:
            from rag.memory_store import add_filing
            add_filing(filing_id, ticker, company_name, filing_type, summary, significance_score, filed_at)
            return True
        except Exception as e:
            logger.error(f"RAG Store MCP call failed: {e}")
            return False
    
    @staticmethod
    def get_history(ticker: str, current_summary: str, n_results: int = 5):
        """Get filing history through MCP server"""
        try:
            from rag.memory_store import get_history
            return get_history(ticker, current_summary, n_results)
        except Exception as e:
            logger.error(f"RAG Retrieve MCP call failed: {e}")
            return []
