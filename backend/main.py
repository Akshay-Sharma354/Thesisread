import os
import io
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from pypdf import PdfReader
from docx import Document

from models import FilingInput
from pipeline import run_pipeline
from rag import memory_store
from services.csv_ingestion import ingest_from_csv
from services.email_service import send_filing_alert, send_test_email
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SEBI Filing Intelligence Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = BackgroundScheduler()

@app.on_event("startup")
def start_scheduler():
    scheduler.start()
    logger.info("Scheduler started")

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/filings/analyze")
def analyze_filing(company_name: str = Form(...), ticker: str = Form(...), raw_text: str = Form(...)):
    if not raw_text.strip():
        raise HTTPException(400, "raw_text is empty")
    try:
        filing = FilingInput(company_name=company_name, ticker=ticker, raw_text=raw_text)
        result = run_pipeline(filing)
        
        significance_score = result.get('significance', {}).get('significance_score', 0)
        if significance_score >= 7:
            alert_email = os.environ.get("ALERT_EMAIL")
            if alert_email:
                send_filing_alert(
                    recipient_email=alert_email,
                    company_name=company_name,
                    ticker=ticker,
                    headline=result.get('alert_headline', ''),
                    body=result.get('alert_body', ''),
                    significance_score=significance_score
                )
        
        return result
    except Exception as e:
        raise HTTPException(500, "Pipeline failed: " + str(e))

@app.post("/filings/upload")
async def upload_filing(company_name: str = Form(...), ticker: str = Form(...), file: UploadFile = File(...)):
    filename = file.filename.lower()
    
    try:
        contents = await file.read()
        text = ""
        
        if filename.endswith('.pdf'):
            reader = PdfReader(io.BytesIO(contents))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif filename.endswith('.docx'):
            doc = Document(io.BytesIO(contents))
            text = "\n".join(para.text for para in doc.paragraphs)
        elif filename.endswith('.txt'):
            text = contents.decode('utf-8')
        else:
            raise HTTPException(400, "Supported formats: PDF, DOCX, TXT")
        
        text = text.strip()
        if not text:
            raise HTTPException(422, "Could not extract text from file")
        
        filing = FilingInput(company_name=company_name, ticker=ticker, raw_text=text)
        result = run_pipeline(filing)
        
        significance_score = result.get('significance', {}).get('significance_score', 0)
        if significance_score >= 7:
            alert_email = os.environ.get("ALERT_EMAIL")
            if alert_email:
                send_filing_alert(
                    recipient_email=alert_email,
                    company_name=company_name,
                    ticker=ticker,
                    headline=result.get('alert_headline', ''),
                    body=result.get('alert_body', ''),
                    significance_score=significance_score
                )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, "Upload failed: " + str(e))

@app.post("/ingest/csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Only CSV files are supported")
    
    try:
        contents = await file.read()
        csv_content = contents.decode('utf-8')
        result = ingest_from_csv(csv_content)
        return result
    except Exception as e:
        raise HTTPException(500, "CSV ingestion failed: " + str(e))

@app.post("/alerts/test-email")
def test_email(email: str = Form(...)):
    """Test email alert system"""
    try:
        success = send_test_email(email)
        if success:
            return {"status": "success", "message": "Test email sent! Check your inbox."}
        else:
            return {"status": "error", "message": "Failed to send test email. Check email credentials."}
    except Exception as e:
        raise HTTPException(500, "Test email failed: " + str(e))

@app.get("/alerts")
def get_alerts(limit: int = 50):
    return memory_store.all_recent(limit=limit)

@app.get("/companies/{ticker}/history")
def company_history(ticker: str):
    all_rows = memory_store.all_recent(limit=500)
    return [r for r in all_rows if r.get("ticker", "").upper() == ticker.upper()]

@app.get("/scheduler/status")
def scheduler_status():
    return {
        "running": scheduler.running,
        "jobs": [{"id": job.id, "name": job.name} for job in scheduler.get_jobs()]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
