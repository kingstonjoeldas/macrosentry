# MacroSentry Setup Guide

This is a complete, production-grade autonomous Fed/market surveillance pipeline. Follow these steps to get it running.

## Step 1: Install Dependencies

```bash
# From the project root directory
pip install -r requirements.txt
```

**Note:** `sentence-transformers` will download embeddings (~100MB). This happens once on first run.

If you have issues, install core dependencies first:
```bash
pip install requests beautifulsoup4 pydantic python-dotenv
pip install sentence-transformers streamlit pandas numpy pytz
```

## Step 2: Configure Environment

Create a `.env` file (or copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your API keys:
- **HUGGINGFACE_API_KEY**: Optional (free tier doesn't require auth)
- **SUPABASE_URL**: Get from https://supabase.com (free tier)
- **SUPABASE_KEY**: From Supabase dashboard
- **ALPHA_VANTAGE_API_KEY**: Get from https://www.alphavantage.co (free tier)

All services have free tiers with no credit card required.

## Step 3: Verify Installation

```bash
# Test basic imports
python -c "from src.macrosentry.types import RawEvent; print('OK')"

# Test individual components
python -m macrosentry test ingestion
python -m macrosentry test rag
python -m macrosentry test classification
python -m macrosentry test evaluation
python -m macrosentry test storage
```

## Step 4: Run the Pipeline

```bash
# Run full pipeline once
python -m macrosentry run

# This will:
# 1. Ingest events (Fed statements, news, calendar)
# 2. Classify each event (hawkish/dovish, impact tier)
# 3. Evaluate (check price movements)
# 4. Store results in mock database
# 5. Print summary
```

Expected output:
```
======================================================================
MacroSentry Pipeline Result
======================================================================
Run ID: <uuid>
Events Processed: 25
Accuracy: 72.0%
Errors: 0

Dashboard Summary:
  Overall Bias: DOVISH
    Hawkish: 5
    Dovish: 12
    Neutral: 8
  Self-eval Accuracy: 72.0%
  Total Runs: 1
  Recent Events: 25
======================================================================
```

## Step 5: Run Dashboard

```bash
# Start Streamlit dashboard locally
python -m macrosentry dashboard

# Opens on http://localhost:8501
```

You'll see:
- Today's overall bias (hawkish/dovish/neutral)
- Self-evaluation accuracy percentage
- Live event feed with classifications and results
- Pipeline run history
- Configuration overview

## Step 6: Deploy to Production

### Option A: Deploy Dashboard to Streamlit Cloud

1. Push this repo to GitHub
2. Go to https://streamlit.io/cloud
3. "New app" → Select your repo
4. Main file: `dashboard/app.py`
5. Add secrets from `.env` in the app settings
6. Deploy — your dashboard is now live at a public URL

### Option B: Schedule Pipeline Runs

GitHub Actions will run the pipeline automatically on a schedule:

1. Add secrets to your GitHub repo:
   - `HUGGINGFACE_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `ALPHA_VANTAGE_API_KEY`

2. Default schedule: Every 6 hours (edit `.github/workflows/pipeline.yml` to change)

3. Each run:
   - Fetches Fed statements and economic events
   - Classifies them
   - Checks price movements
   - Scores accuracy
   - Saves to Supabase (displayed on dashboard)

## Troubleshooting

### "ModuleNotFoundError: No module named 'X'"

```bash
pip install requests beautifulsoup4 sentence-transformers streamlit
```

### "sentence-transformers downloading model" (stuck)

This is normal on first run. The model is ~100MB. Wait a few minutes.

To skip this and use a different model, edit `src/macrosentry/rag.py`:
```python
def __init__(self, model_name: str = "all-MiniLM-L6-v2"):  # Change this line
```

Smaller models:
- `"all-MiniLM-L6-v2"` (22M parameters, fastest)
- `"paraphrase-MiniLM-L6-v2"` (33M parameters)

### "SUPABASE_URL not found in .env"

Create `.env` with your Supabase credentials:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

Get these from: https://supabase.com → Create project → Settings → API Keys

### "No events fetched"

The ingestion module fetches from:
- federalreserve.gov (public, no auth needed)
- Mock economic calendar
- Mock news aggregator

In production, integrate real APIs:
- NewsAPI: https://newsapi.org
- FRED: https://fred.stlouisfed.org (economic data)
- Alpha Vantage: https://www.alphavantage.co (price data)

See `src/macrosentry/ingestion.py` for integration points.

## Project Structure Quick Reference

```
MacroSentry/
├── src/macrosentry/
│   ├── pipeline.py        ← Main orchestrator (run this)
│   ├── ingestion.py       ← Fetch events
│   ├── rag.py             ← Historical context retrieval
│   ├── classification.py  ← Classify events
│   ├── evaluation.py      ← Check predictions
│   ├── storage.py         ← Save to database
│   ├── observability.py   ← Structured logging
│   └── cli.py             ← Command-line interface
├── dashboard/app.py       ← Streamlit UI
├── .github/workflows/pipeline.yml  ← GitHub Actions scheduler
└── tests/                 ← Unit tests
```

## Commands

```bash
# Run pipeline
python -m macrosentry run

# Start dashboard
python -m macrosentry dashboard --port 8501

# Test components
python -m macrosentry test ingestion
python -m macrosentry test rag
python -m macrosentry test classification
python -m macrosentry test evaluation
python -m macrosentry test storage

# Direct Python
python -m macrosentry.pipeline  # Run pipeline
python -m macrosentry.ingestion # Test ingestion
python -m macrosentry.rag       # Test RAG
python dashboard/app.py         # Run dashboard
```

## Next Steps

1. ✅ Finish setup above
2. Run pipeline: `python -m macrosentry run`
3. View dashboard: `python -m macrosentry dashboard`
4. Deploy to Streamlit Cloud
5. Enable GitHub Actions scheduled runs
6. Monitor accuracy over time
7. Integrate real data APIs (Fed, Alpha Vantage, etc.)

## Cost Check

| Component | Monthly Cost |
|-----------|--------------|
| Hugging Face | $0 (free tier) |
| Supabase | $0 (free tier) |
| GitHub Actions | $0 (2000 min/month free) |
| Streamlit Cloud | $0 (free tier) |
| **Total** | **$0** |

You never pay anything to run this project.
