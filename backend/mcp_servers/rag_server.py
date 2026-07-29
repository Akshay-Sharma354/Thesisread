"""
RAG Memory MCP Server - manages filing history and pattern detection
"""
import json
import logging
from mcp.server import Server
from mcp.types import TextContent

logger = logging.getLogger(__name__)

server = Server("thesisread-rag-service")

@server.call_tool()
def store_filing(filing_id: str, ticker: str, company_name: str, filing_type: str, summary: str, significance_score: int, filed_at: str):
    """Store a filing in memory"""
    from rag.memory_store import add_filing
    
    try:
        add_filing(filing_id, ticker, company_name, filing_type, summary, significance_score, filed_at)
        return TextContent(type="text", text=f"Filing stored for {ticker}")
    except Exception as e:
        logger.error(f"RAG Store error: {e}")
        return TextContent(type="text", text=f"Error: {str(e)}")

@server.call_tool()
def get_filing_history(ticker: str, current_summary: str, n_results: int = 5):
    """Retrieve past filings for pattern detection"""
    from rag.memory_store import get_history
    
    try:
        history = get_history(ticker, current_summary, n_results)
        return TextContent(type="text", text=json.dumps(history))
    except Exception as e:
        logger.error(f"RAG Retrieve error: {e}")
        return TextContent(type="text", text=f"Error: {str(e)}")

@server.call_tool()
def get_all_alerts(limit: int = 50):
    """Get all analyzed filings"""
    from rag.memory_store import all_recent
    
    try:
        alerts = all_recent(limit)
        return TextContent(type="text", text=json.dumps(alerts))
    except Exception as e:
        return TextContent(type="text", text=f"Error: {str(e)}")

if __name__ == "__main__":
    server.run()
