# ThesisRead

**AI-powered corporate filing analyzer for Indian stock investors.**

Every day, 50+ new corporate filings appear on NSE/BSE. Most investors skip them because they're written in impenetrable regulatory jargon and reading one takes 30+ minutes. **ThesisRead changes that.**

We use multi-agent AI to instantly read filings, explain them in plain English, score their significance (1-10), and detect patterns across time that signal material changes in a company's profile.

---

## The Problem: Why Retail Investors Miss Critical Filings

### Current State
- **50+ new filings daily** on NSE/BSE across 2,000+ listed companies
- **Jargon barrier** — "Regulation 30, SEBI LODR disclosure of material event" is meaningless to 99% of retail investors
- **Time barrier** — reading + analyzing a single filing takes 30+ minutes
- **Context loss** — each filing analyzed alone misses patterns
- **Pattern blindness** — what looks routine ("another related-party deal") is actually a red flag when it's the 3rd one in 18 months

### Real Examples of What Gets Missed
1. **Auditor Resignation** — looked routine, but was the 3rd auditor change in 2 years (governance red flag)
2. **Related-Party Transactions** — single deal looks fine, but 4 similar deals in 6 months shows MD self-dealing pattern
3. **Guidance Changes** — company cuts revenue guidance but files look "operational" at first glance
4. **Promoter Pledging** — each small pledge looks minor, but cumulatively it signals financial stress

**Result:** Retail investors miss material signals. Institutional investors (with research teams) catch them. Information asymmetry favors the rich.

---

## The Solution: ThesisRead

ThesisRead is a **4-agent AI system** that reads corporate filings the way a professional equity analyst would:

### How It Works

**Input:** Raw filing text (from PDF, DOCX, TXT, CSV, or manual paste)

**Processing (4 AI Agents):**

1. **Extraction Agent**
   - Reads the filing
   - Identifies: filing type, key entities, amounts, dates
   - Generates plain-English summary
   - *Cost: 1 Claude call*

2. **Significance Agent**
   - Scores 1-10 from shareholder perspective
   - Classifies sentiment (positive/negative/neutral/mixed)
   - Flags risks and opportunities
   - *Cost: 1 Claude call*

3. **Comparator Agent** ← **The Differentiator**
   - Retrieves past filings for this ticker from memory (RAG)
   - Detects patterns ("3rd auditor change in 18 months")
   - Notes contradictions with prior guidance
   - Spots recurring behaviors (MD-linked self-dealing)
   - *Cost: 1 Claude call (only if history exists)*

4. **Alert Agent**
   - Synthesizes final headline + body
   - Explains *why* it matters, not just *what* happened
   - Targets retail investor comprehension level
   - *Cost: 1 Claude call*

**Output:** Scored, contextualized alert ready for a dashboard or email

### Example Pipeline in Action

**Raw Filing:**
```
Disclosure under Regulation 23(9) of SEBI LODR - Related Party Transaction

Reliance Industries Limited has approved a material related party transaction 
whereby the company will procure electronic components from Reliance Components 
Limited (entity in which promoter family holds 45% stake) for an aggregate value 
not exceeding Rs. 500 crore for FY 2026-27.
```

**Agent 1 (Extraction):**
- Filing type: "Related Party Transaction"
- Key entities: Reliance Industries, Reliance Components Limited, promoter family
- Amount: Rs. 500 crore
- Summary: "Reliance approves Rs 500 crore procurement from promoter-linked company"

**Agent 2 (Significance):**
- Score: 6/10 (material but flagged as "arm's length")
- Sentiment: Mixed
- Risk flags: ["Related-party deal", "No independent valuation mentioned"]
- Opportunity flags: None

**Agent 3 (Comparator):**
- Past 6 months: Found 2 previous related-party deals from same promoter entity
- Pattern: "3rd major related-party transaction in 6 months from same entity"
- Note: "Recurring pattern suggests systematic self-dealing"

**Agent 4 (Alert):**
- Headline: "Reliance approves Rs 500 crore component purchase from promoter-linked firm (3rd in 6mo)"
- Body: "This is the third major related-party deal with the same promoter entity in six months. While the company claims arm's-length pricing, the lack of independent valuation and recurring nature warrant closer scrutiny of governance practices."

**Dashboard Display:**
```
RELIANCE · RELATED PARTY TRANSACTION · 2026-07-28
6/10

Reliance approves Rs 500 crore component purchase from promoter-linked firm (3rd in 6mo)

This is the third major related-party deal with the same promoter entity in 
six months. While the company claims arm's-length pricing, the lack of 
independent valuation and recurring nature warrant closer scrutiny of 
governance practices.

Pattern: Recurring related-party transactions with promoter entities
```

---

## Why This Matters

### For Retail Investors
- **Democratizes access** to analysis that only institutional investors get
- **Saves 30+ minutes per filing** — instant plain-English explanation
- **Catches patterns** that single-filing analysis misses
- **Levels the playing field** against institutional information advantage

### For the Market
- **Better information distribution** reduces mispricing
- **Earlier signal detection** on governance red flags
- **Retail participation increases** when filings become understandable

---

## The Tech Stack

**Backend:**
- FastAPI (Python)
- Claude AI (Anthropic API) — 4 specialized agents
- Chroma (vector database) — RAG memory of past filings
- APScheduler (background tasks)

**Frontend:**
- HTML/CSS/JavaScript (vanilla)
- Professional dark-themed dashboard

**Data Ingestion:**
- CSV bulk upload
- PDF/DOCX/TXT file upload
- Manual filing paste
- (Soon: NSE/BSE live scraper)

---

## Quick Start

### Prerequisites
- Python 3.11+
- Anthropic API key ([get one free](https://console.anthropic.com))

### Installation

```bash
# Clone
git clone https://github.com/Akshay-Sharma354/thesisread.git
cd thesisread

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Configure
cd backend
cp .env.example .env
# Edit .env: add your ANTHROPIC_API_KEY
```

### Run

**Terminal 1 — API:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```
Runs on `http://localhost:8000`

**Terminal 2 — Frontend:**
```bash
cd frontend
python3 -m http.server 3000
```
Open `http://localhost:3000`

### Test

1. **Paste text:** Go to "Paste Text" tab, paste a filing, click Analyze
2. **Upload file:** Go to "Upload File" tab, upload PDF/DOCX/TXT
3. **Bulk upload:** Go to "Upload CSV" tab with columns: `company_name, ticker, filing_text, filed_at`

---

## Project Structure

```
thesisread/
├── backend/
│   ├── main.py                   # FastAPI app
│   ├── pipeline.py               # Orchestrates 4 agents
│   ├── config.py                 # Config + Claude client
│   ├── models.py                 # Data schemas
│   ├── requirements.txt
│   ├── agents/
│   │   ├── extraction_agent.py   # Agent 1: Extraction
│   │   ├── significance_agent.py # Agent 2: Significance scoring
│   │   ├── comparator_agent.py   # Agent 3: Pattern detection (RAG)
│   │   ├── alert_agent.py        # Agent 4: Alert composition
│   │   └── json_agent.py         # Shared JSON helper
│   ├── rag/
│   │   └── memory_store.py       # Chroma vector store for filing history
│   ├── services/
│   │   └── csv_ingestion.py      # CSV processor
│   └── sample_data/              # Example filings for demo
│
├── frontend/
│   ├── index.html                # Dashboard UI
│   ├── app.js                    # Frontend logic
│   └── style.css                 # Dark-themed styling
│
├── README.md
├── LICENSE (MIT)
└── .gitignore
```

---

## How It Compares

| Feature | ThesisRead | Screener.in | Trendlyne | Ticker |
|---------|-----------|-----------|-----------|--------|
| AI-powered explanation | ✅ | ❌ | ⚠️ Basic | ❌ |
| Pattern detection across filings | ✅ | ❌ | ❌ | ❌ |
| Plain English summaries | ✅ | ❌ | ❌ | ⚠️ |
| Significance scoring (1-10) | ✅ | ❌ | ❌ | ⚠️ |
| Open source | ✅ | ❌ | ❌ | ❌ |
| Cost | Free (pay API) | ₹99/mo | ₹299/mo | ₹199/mo |

---

## API Endpoints

**POST `/filings/analyze`** — Analyze pasted text
```bash
curl -X POST http://localhost:8000/filings/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Reliance Industries",
    "ticker": "RELIANCE",
    "raw_text": "Board approved Rs 10000 crore investment in renewable energy..."
  }'
```

**POST `/filings/upload`** — Upload PDF/DOCX/TXT
```bash
curl -X POST http://localhost:8000/filings/upload \
  -F "company_name=Reliance" \
  -F "ticker=RELIANCE" \
  -F "file=@filing.pdf"
```

**POST `/ingest/csv`** — Bulk upload from CSV
```bash
curl -X POST http://localhost:8000/ingest/csv \
  -F "file=@filings.csv"
```

**GET `/alerts`** — Get all analyzed filings
```bash
curl http://localhost:8000/alerts?limit=50
```

**GET `/companies/{ticker}/history`** — Filing history for one company
```bash
curl http://localhost:8000/companies/RELIANCE/history
```

---

## Environment Setup

Create `.env` in `backend/`:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
FAST_MODEL=claude-haiku-4-5-20251001
REASONING_MODEL=claude-sonnet-5
```

---

## Roadmap

### Phase 1 ✅ (Complete)
- 4-agent AI pipeline
- RAG memory + pattern detection
- File upload (PDF, DOCX, TXT)
- CSV bulk ingestion
- Dashboard with 3 input methods

### Phase 2 (Next)
- User authentication & accounts
- Personal watchlists (track specific tickers)
- Email/SMS alerts on high-significance filings
- Production deployment (Railway/Vercel)

### Phase 3 (Planned)
- NSE/BSE live scraper (respecting ToS)
- Industry peer comparison
- Institutional research integration
- Mobile app (React Native)

---

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push and open a Pull Request

---

## License

MIT License — see LICENSE file

---

## Contact & Social

- **GitHub:** [@Akshay-Sharma354](https://github.com/Akshay-Sharma354)
- **Twitter:** [@yoursocialhandle](https://twitter.com)
- **Email:** your.email@example.com

---

## Acknowledgments

Built with ❤️ for retail investors in India who deserve better access to investment intelligence.

**Powered by:**
- [Claude AI](https://anthropic.com) — Multi-agent orchestration
- [Chroma](https://www.trychroma.com/) — Vector storage for RAG
- [FastAPI](https://fastapi.tiangolo.com/) — Lightning-fast API framework
- [MIT License](https://opensource.org/licenses/MIT) — Open source spirit
