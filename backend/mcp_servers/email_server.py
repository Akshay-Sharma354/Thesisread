"""
Email Alert MCP Server - handles all email notifications
"""
import json
import logging
from mcp.server import Server
from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)

# Initialize MCP Server
server = Server("thesisread-email-service")

@server.call_tool()
def send_alert(recipient_email: str, company_name: str, ticker: str, headline: str, body: str, significance_score: int):
    """Send a filing alert via email"""
    from services.email_service import send_filing_alert
    
    try:
        success = send_filing_alert(
            recipient_email=recipient_email,
            company_name=company_name,
            ticker=ticker,
            headline=headline,
            body=body,
            significance_score=significance_score
        )
        
        if success:
            return TextContent(type="text", text=f"Email alert sent to {recipient_email}")
        else:
            return TextContent(type="text", text=f"Failed to send email to {recipient_email}")
    except Exception as e:
        logger.error(f"Email MCP Server error: {e}")
        return TextContent(type="text", text=f"Error: {str(e)}")

@server.call_tool()
def send_test_alert(recipient_email: str):
    """Send a test email"""
    from services.email_service import send_test_email
    
    try:
        success = send_test_email(recipient_email)
        if success:
            return TextContent(type="text", text=f"Test email sent to {recipient_email}")
        else:
            return TextContent(type="text", text="Failed to send test email")
    except Exception as e:
        return TextContent(type="text", text=f"Error: {str(e)}")

if __name__ == "__main__":
    server.run()
