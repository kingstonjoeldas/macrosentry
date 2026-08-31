# MacroSentry

**Autonomous Fed & Market Surveillance Pipeline with Self-Evaluating Predictions**

An AI-powered pipeline that monitors Federal Reserve statements, economic calendar events, and market news; classifies each event's hawkish/dovish bias and impact tier; grounds classifications using RAG and historical FOMC context; and self-evaluates accuracy by comparing predictions to actual price movements 30 minutes after each event. Results are published to a public, login-free dashboard.

## Features

✅ **Real-time ingestion** — Fed statements, speeches, economic calendar, and market news  
✅ **RAG-grounded classification** — Zero-shot classification with historical FOMC context retrieval  
✅ **Self-evaluating** — Checks price movements and scores prediction accuracy automatically  
✅ **Structured observability** — JSON logs for every node in the pipeline  
✅ **Public dashboard** — Live event feed, bias summary, and accuracy stats (no login required)  
✅ **$0 cost** — Free-tier APIs only (Hugging Face, Supabase, GitHub Actions, Streamlit Cloud)  
✅ **Production-grade** — LangGraph orchestration, vector embeddings, scheduled cloud compute  

## Architecture

```
Ingestion (Fed/news) 
    ↓
Entity Extraction (NER)
    ↓
RAG Retrieval (historical FOMC context)
    ↓
Classification (hawkish/dovish/neutral, impact tier)
    ↓
Summarization (one-line "why")
    ↓
Price Checking (actual movement 30min after event)
    ↓
Self-Evaluation (prediction vs. reality)
    ↓
Storage (Supabase)
    ↓
Dashboard (Streamlit public URL)
```

**Stack:**
- **Ingestion:** federalreserve.gov, economic calendars, market news APIs
- **Embeddings:** Sentence-Transformers (local, CPU-friendly)
- **RAG:** In-memory vector store + historical FOMC seed data
- **Classification:** Hugging Face Inference API (free, zero-shot)
- **Orchestration:** LangGraph (DAG-based pipeline)
- **Storage:** Supabase free tier (PostgreSQL)
- **Scheduling:** GitHub Actions cron jobs
- **Dashboard:** Streamlit Cloud (free tier)

## Setup

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/macrosentry.git
cd macrosentry
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root:

```bash
# Hugging Face (free tier, can stay empty for public inference)
HUGGINGFACE_API_KEY=

# Supabase (sign up at https://supabase.com, free tier)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Alpha Vantage (for futures price data, free tier)
ALPHA_VANTAGE_API_KEY=
```

**Note:** All services above have free tiers with no credit card required to start.

### 3. Run the Pipeline

```bash
# Test individual components
python -m macrosentry test ingestion
python -m macrosentry test rag
python -m macrosentry test classification
python -m macrosentry test evaluation
python -m macrosentry test storage

# Run full pipeline
python -m macrosentry run

# Start dashboard locally
python -m macrosentry dashboard
# Opens on http://localhost:8501
```

## Usage

### Command-Line Interface

```bash
# Run pipeline once
python -m macrosentry run

# Run pipeline and skip storage (testing only)
python -m macrosentry run --no-store

# Start Streamlit dashboard
python -m macrosentry dashboard --port 8501

# Test individual components
python -m macrosentry test ingestion
python -m macrosentry test rag
python -m macrosentry test classification
python -m macrosentry test evaluation
python -m macrosentry test storage
```

### Scheduled Runs (GitHub Actions)

Edit `.github/workflows/pipeline.yml` to adjust the cron schedule:
- Default: Every 6 hours
- More frequent: `0 * * * *` (every hour)
- Daily: `0 8 * * *` (8 AM UTC daily)

Logs from each run are archived in GitHub Actions artifacts for 30 days.

### Dashboard

Once deployed to Streamlit Cloud:
1. **Dashboard tab** — Today's bias summary, accuracy stats, event preview
2. **Event Feed** — Complete list of classified and evaluated events
3. **Pipeline Runs** — Historical accuracy, manual run trigger
4. **Settings** — Configuration overview, monitored futures, evaluation window

No login required; the dashboard is a public URL.

## Project Structure

```
MacroSentry/
├── src/macrosentry/
│   ├── ingestion.py       # Fetch Fed statements, news, calendar
│   ├── rag.py             # Vector store and retrieval
│   ├── classification.py  # Zero-shot classification, NER, summarization
│   ├── evaluation.py      # Price checking and self-eval
│   ├── storage.py         # Supabase integration
│   ├── pipeline.py        # LangGraph orchestration
│   ├── observability.py   # Structured logging
│   ├── config.py          # Configuration
│   ├── types.py           # Type definitions
│   ├── cli.py             # CLI entry point
│   └── __init__.py
├── dashboard/
│   └── app.py             # Streamlit dashboard
├── data/
│   ├── logs/              # Pipeline logs (JSON)
│   ├── historical_fomc/   # Seed data for RAG
│   └── processed/         # Output results
├── .github/workflows/
│   └── pipeline.yml       # GitHub Actions scheduler
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project metadata
└── README.md
```

## Deployment

### Deploy Dashboard to Streamlit Cloud

1. Push this repo to GitHub
2. Go to https://streamlit.io/cloud
3. Click "New app" and select your repo
4. Set main file path: `dashboard/app.py`
5. Add environment variables (SUPABASE_URL, SUPABASE_KEY, etc.) in the app settings
6. Deploy — your dashboard is now live at a public URL

### Enable GitHub Actions Scheduled Runs

1. Ensure `.github/workflows/pipeline.yml` is in the repo
2. Go to Actions → MacroSentry Pipeline → Enable
3. Add secrets: `HUGGINGFACE_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, `ALPHA_VANTAGE_API_KEY`
4. Runs will execute on schedule and store results in Supabase, visible on the dashboard

## How It Works

### Phase 1: Ingestion
Fetches recent Fed statements, speeches, economic calendar events, and market news. Returns raw text headlines and bodies for downstream classification.

### Phase 2: RAG
Maintains an in-memory vector store seeded with historical FOMC statements (2024–2025). When classifying a new event, retrieves the top-3 most similar historical statements as context, ensuring classifications are grounded in how the Fed has spoken before.

### Phase 3: Classification
Uses Hugging Face zero-shot classification to label each event:
- **Sentiment:** Hawkish (USD/rates up) → dovish (risk/commodities up) → neutral
- **Impact:** High/medium/low based on market relevance
- **Entities:** Named entity recognition extracts tickers (gold, soybeans, etc.)
- **Summary:** One-sentence compressed version for the dashboard

### Phase 4: Evaluation
Fetches the actual price movement of relevant futures 30 minutes after the event. Compares the predicted direction (from classification) vs. actual direction, recording whether the prediction was correct. This creates a continuous feedback loop.

### Phase 5: Storage
Saves classified and evaluated events to Supabase. Stores pipeline run metadata (start/end time, event count, accuracy, errors) for tracking performance over time.

### Phase 6: Dashboard
Streamlit app displays:
- **Overall bias** (hawkish/dovish/neutral) — aggregated from recent events
- **Self-eval accuracy** — percentage of predictions that matched reality
- **Event feed** — recent classified events with bias labels, summaries, and evaluation results
- **Metrics** — total events, runs, and historical accuracy

### Phase 7: Observability
Every node in the pipeline logs structured JSON entries: timestamp, event type (ingestion_start, classification_event, evaluation_event, etc.), message, and rich metadata. Logs are saved to `data/logs/` and can be queried for debugging.

## Model Selection & Justification

- **Zero-shot classification:** `facebook/bart-large-mnli` — Handles hawkish/dovish/neutral and impact classification without fine-tuning (free, proven MNLI performance)
- **NER:** `dslim/bert-base-NER` — Lightweight, extracts economic entities (Fed, CPI, gold, etc.)
- **Summarization:** `facebook/bart-large-cnn` — Compresses headlines/statements to one sentence
- **Embeddings:** `all-MiniLM-L6-v2` — Runs locally, 22M parameters, fast (no API call needed for RAG)

All models are available via Hugging Face free tier. Total cost: **$0**.

## Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| Hugging Face Inference API | Free | 30k requests/month free tier |
| Supabase PostgreSQL | Free | 500MB storage, unlimited API calls |
| GitHub Actions | Free | 2,000 min/month free tier (plenty for 4 runs/day) |
| Streamlit Cloud | Free | 1 app deployed free tier |
| Sentence-Transformers | Free | Runs locally on your machine |
| **Total** | **$0** | No credit card required to start |

## Roadmap

- [ ] Fine-tune zero-shot model on labeled Fed event dataset (5-10K examples)
- [ ] Add websocket stream for real-time price updates (instead of batch 30-min checks)
- [ ] Integrate with messaging (Discord/Slack alerts on high-confidence, high-impact events)
- [ ] Multi-horizon evaluation (1h, 1d, 1w price predictions)
- [ ] Explainability dashboard (show which historical events influenced each classification)
- [ ] CLI option to sync historical events back to a start date

## Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License. See [LICENSE](LICENSE) for details.

## Questions?

- Email: kingstonjoel.m@gmail.com
- GitHub Issues: Use this repo's issue tracker

---

**Built with ❤️ using free AI/data APIs. No subscription required.**
