"""
Email alert service - sends alerts when filings score 7+/10
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

logger = logging.getLogger(__name__)

def send_filing_alert(recipient_email: str, company_name: str, ticker: str, headline: str, body: str, significance_score: int):
    """
    Send email alert for a high-significance filing
    """
    sender_email = os.environ.get("ALERT_EMAIL")
    sender_password = os.environ.get("ALERT_EMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        logger.warning("Email credentials not configured. Skipping email alert.")
        return False
    
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "[" + str(significance_score) + "/10] " + company_name + " (" + ticker + "): " + headline
        message["From"] = sender_email
        message["To"] = recipient_email
        
        text = "ThesisRead Filing Alert\n\nCompany: " + company_name + " (" + ticker + ")\nSignificance: " + str(significance_score) + "/10\n\n" + headline + "\n\n" + body + "\n\n---\nThis is an automated alert from ThesisRead."
        
        html = "<html><body><h2>ThesisRead Filing Alert</h2><p><b>Company:</b> " + company_name + " (" + ticker + ")</p><p><b>Significance:</b> " + str(significance_score) + "/10</p><h3>" + headline + "</h3><p>" + body + "</p></body></html>"
        
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        
        message.attach(part1)
        message.attach(part2)
        
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        
        logger.info("Email alert sent to " + recipient_email + " for " + company_name)
        return True
    
    except Exception as e:
        logger.error("Failed to send email alert: " + str(e))
        return False

def send_test_email(recipient_email: str):
    """
    Send a test email to verify setup
    """
    return send_filing_alert(
        recipient_email=recipient_email,
        company_name="Test Company",
        ticker="TEST",
        headline="This is a test alert from ThesisRead",
        body="If you received this email, your alert system is working correctly!",
        significance_score=8
    )
