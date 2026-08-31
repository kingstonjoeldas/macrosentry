# 🚀 MacroSentry Quick Start

**3 commands to run the full project locally.**

## 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
Takes ~5 minutes (sentence-transformers model download).

## 2️⃣ Run Pipeline
```bash
python -m macrosentry run
```

**Output:**
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

## 3️⃣ View Dashboard
```bash
python -m macrosentry dashboard
```
Opens on **http://localhost:8501**

---

## Deploy to Production

See **[DEPLOY.md](DEPLOY.md)** for:
- ✅ Deploy dashboard to Streamlit Cloud (5 min)
- ✅ Enable GitHub Actions scheduled runs (2 min)
- ✅ Monitor accuracy over time

---

## Test Individual Components

```bash
# Test ingestion
python -m macrosentry test ingestion

# Test RAG
python -m macrosentry test rag

# Test classification
python -m macrosentry test classification

# Test evaluation
python -m macrosentry test evaluation

# Test storage
python -m macrosentry test storage
```

---

## File Structure

| File | Purpose |
|------|---------|
| `src/macrosentry/pipeline.py` | Main orchestrator |
| `src/macrosentry/ingestion.py` | Fetch events |
| `src/macrosentry/rag.py` | Historical context |
| `src/macrosentry/classification.py` | Classify events |
| `src/macrosentry/evaluation.py` | Check predictions |
| `src/macrosentry/storage.py` | Save to database |
| `dashboard/app.py` | Web UI |
| `.github/workflows/pipeline.yml` | Scheduled runs |

---

## What It Does

1. **Fetches** Fed statements, speeches, economic calendar, market news
2. **Classifies** each event (hawkish/dovish/neutral, high/medium/low impact)
3. **Grounds** classifications using RAG + historical FOMC context
4. **Checks** price movements 30 minutes after event
5. **Scores** accuracy (prediction vs. actual)
6. **Displays** results on public dashboard
7. **Schedules** automatic runs every 6 hours

---

## Cost

**$0** — Everything is free tier (Hugging Face, Supabase, GitHub Actions, Streamlit Cloud)

---

## API Keys Needed

All free, no credit card:
- ✅ Hugging Face (optional, free inference)
- ✅ Supabase (free PostgreSQL)
- ✅ Alpha Vantage (free price data)

See `.env.example` for format.

---

## Help

- **Full docs:** [README.md](README.md)
- **Deployment:** [DEPLOY.md](DEPLOY.md)
- **Setup:** [SETUP.md](SETUP.md)
- **Project brief:** [CLAUDE.md](CLAUDE.md)

---

**Done!** You now have a production-grade AI pipeline running Fed/market surveillance. 🎯
