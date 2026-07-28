# SEBI Filing Intelligence Agent

An MVP that reads SEBI/NSE/BSE corporate filings, explains them in plain English, scores how
much they actually matter, and — the differentiating part — remembers every past filing for a
company so a new one can be compared against its history (repeated related-party deals, auditor
churn, contradicted guidance, etc.).

## How it's built

```
Raw filing text
      │
      ▼
[Extraction Agent]     → filing type, key entities, plain-English summary
      │
      ▼
[Significance Agent]   → 1-10 score, sentiment, risk/opportunity flags
      │
      ▼
[Comparator Agent] ◄── [RAG memory: past filings for this ticker, via Chroma]
      │                  retrieves + compares against everything seen before
      ▼
[Alert Agent]           → final headline + body a retail investor actually reads
      │
      ▼
Stored back into RAG memory (so it's history for the NEXT filing)
```

Each agent is a separate, single-purpose Claude call (`backend/agents/`) rather than one giant
prompt — this is what lets you tune, test, and swap each step independently, and it's the same
pattern as a proper multi-agent pipeline rather than a single "summarize this" call.

The comparator agent is what makes this different from a filing summarizer: every new filing for
a ticker is checked against everything stored before it, so patterns across filings (not just
within one) get surfaced.

## Project layout

```
backend/
  main.py              FastAPI app (the API the frontend calls)
  pipeline.py           orchestrates the 4 agents in order
  config.py              model/client config, reads ANTHROPIC_API_KEY
  models.py               shared Pydantic schemas
  agents/                one file per agent
  rag/memory_store.py      Chroma-backed long-term memory per ticker
  sample_data/             5 synthetic filings to demo with (no real data source wired up yet)
  seed_sample_data.py       runs all sample filings through the pipeline in order
frontend/
  index.html / app.js / style.css     plain HTML/JS dashboard (paste a filing, see the alert feed)
```

## Setup

```bash
cd backend
pip install -r requirements.txt --break-system-packages   # or use a venv
cp .env.example .env
# edit .env and add your ANTHROPIC_API_KEY
```

Run the demo data through the pipeline first (populates the dashboard with 5 analyzed filings,
including the GreenHarvest Agro pair that demonstrates pattern detection):

```bash
python seed_sample_data.py
```

Start the API:

```bash
uvicorn main:app --reload
```

Open `frontend/index.html` directly in a browser (or serve it with `python -m http.server` from
the `frontend/` folder). It talks to the API at `http://localhost:8000`.

## What's real vs. what's a placeholder right now

- **Real**: the full 4-agent pipeline, the RAG comparator, the FastAPI backend, the PDF upload
  endpoint (`/filings/analyze-pdf`), the dashboard.
- **Placeholder**: the 5 sample filings are synthetic text I wrote to exercise every filing type
  (routine results, repeated related-party transactions, an auditor resignation, a boring
  compliance certificate) — not real NSE/BSE filings.

## The next real decision: where filings come from

NSE and BSE's own sites restrict automated/commercial scraping in their terms of use. Before this
can run on live data at any scale, you need one of:

1. **A licensed data vendor** (Trendlyne, Tijori Finance, or an Apify-style filing monitor) —
   fastest path, costs money, keeps you clearly on the right side of ToS.
2. **NSE's single-filing API integration** — this exists for *listed companies* to file once and
   have it propagate to both exchanges; it's not a public read API for third parties, so it
   doesn't solve your ingestion problem directly, but worth knowing it exists.
3. **Manual/personal-use pulls from public filing pages** — fine for prototyping (which is what
   the sample data stands in for here), not fine as the backbone of a product you'd charge for.

Once you've picked one, the only code that changes is a new "fetch new filings" step that calls
`FilingInput(...)` and `run_pipeline(...)` — everything downstream is already built.

## Known limitations (MVP-honest)

- No auth, no user accounts, no watchlists yet — the dashboard shows everything for everyone.
- No scheduler/poller — filings are analyzed one at a time, on demand.
- No de-duplication if the same filing gets submitted twice.
- Chroma's default embedding function is fine for a demo; a stronger embedding model would help
  once you have real filing volume across hundreds of tickers.
