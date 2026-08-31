# MacroSentry Deployment Guide

Complete steps to deploy MacroSentry to production with automated scheduling.

## Quick Deploy (5 minutes)

### 1. Deploy Dashboard to Streamlit Cloud

1. **Push to GitHub:**
   ```bash
   git push origin main
   ```

2. **Go to Streamlit Cloud:**
   - Visit https://streamlit.io/cloud
   - Click "New app"
   - Select your GitHub repo
   - Set main file: `dashboard/app.py`
   - Click "Deploy"

3. **Add Secrets** (in Streamlit Cloud app settings):
   ```
   HUGGINGFACE_API_KEY = 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
   SUPABASE_URL = https://ptrqrqximpnyevizhdvl.supabase.co
   SUPABASE_KEY = sb_publishable_Oa6teVvQy2bowKTXO0Q-uw_lvJKM5Mh
   ALPHA_VANTAGE_API_KEY = LZRY7097LV5JLFK5
   ```

4. **Done!** Your dashboard is now live at a public URL.

### 2. Enable Scheduled Pipeline Runs (GitHub Actions)

1. **Add GitHub Secrets:**
   - Go to your GitHub repo → Settings → Secrets and variables → Actions
   - Add these secrets:
     - `HUGGINGFACE_API_KEY`
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
     - `ALPHA_VANTAGE_API_KEY`

2. **Workflow is already configured** in `.github/workflows/pipeline.yml`
   - Default: Runs every 6 hours
   - To change: Edit `.github/workflows/pipeline.yml` and modify the `cron` schedule

3. **Done!** Pipeline auto-runs every 6 hours and saves results to Supabase.

## Full Deployment Checklist

- [ ] API keys are in `.env` (local) and GitHub Secrets (remote)
- [ ] `.env` is in `.gitignore` (don't commit credentials)
- [ ] Dashboard deployed to Streamlit Cloud
- [ ] GitHub Actions workflow enabled (check Actions tab)
- [ ] Run `git push origin main` to trigger first scheduled run
- [ ] Check Streamlit dashboard to see results

## Architecture

```
                 ┌─────────────────────┐
                 │   Your Local PC      │
                 │  (Development)      │
                 └──────────┬──────────┘
                            │
                    ┌───────┴───────┐
                    │               │
                    ▼               ▼
          ┌─────────────────┐  ┌──────────┐
          │  GitHub Repo    │  │  .env    │
          │  (Code, Config) │  │ (Secrets)│
          └────────┬────────┘  └──────────┘
                   │
        ┌──────────┴──────────────┐
        │                         │
        ▼                         ▼
  ┌──────────────┐        ┌──────────────────┐
  │ GitHub       │        │  Streamlit Cloud │
  │ Actions      │        │  (Dashboard)     │
  │ (Scheduler)  │        │  (Public URL)    │
  └──────┬───────┘        └────────┬─────────┘
         │                         │
         └────────────┬────────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │  Supabase PostgreSQL │
            │  (Live Results DB)   │
            └──────────────────────┘
```

## Scheduled Runs

Edit `.github/workflows/pipeline.yml` to change frequency:

**Every 6 hours** (default):
```yaml
- cron: '0 */6 * * *'
```

**Every hour:**
```yaml
- cron: '0 * * * *'
```

**Every day at 8 AM UTC:**
```yaml
- cron: '0 8 * * *'
```

**Every 30 minutes:**
```yaml
- cron: '*/30 * * * *'
```

## Monitor Scheduled Runs

1. Go to your GitHub repo → Actions
2. Select "MacroSentry Pipeline"
3. You'll see each run's status, logs, and artifacts
4. Logs are saved for 30 days

## Troubleshooting

### Dashboard won't load

1. Check Streamlit Cloud logs for errors
2. Verify secrets are set in Streamlit Cloud settings
3. Check `.env` file has correct API keys locally

### Pipeline runs fail

1. Check GitHub Actions logs (Actions tab → MacroSentry Pipeline)
2. Look for specific error messages
3. Verify secrets are set in GitHub repo settings

### Events not appearing in dashboard

1. Run pipeline manually: `python -m macrosentry run`
2. Check Supabase dashboard for data
3. Verify SUPABASE_URL and SUPABASE_KEY are correct

## Cost Check (Production)

| Component | Cost | Notes |
|-----------|------|-------|
| Streamlit Cloud | $0 | Free tier, 1 app |
| GitHub Actions | $0 | Free tier, 2000 min/month |
| Supabase | $0 | Free tier, 500MB storage |
| Hugging Face | $0 | Free inference API |
| **Total** | **$0** | No ongoing costs |

## Next Steps

1. ✅ Deploy dashboard to Streamlit Cloud
2. ✅ Enable GitHub Actions scheduled runs
3. Monitor dashboard for 24 hours
4. Analyze accuracy trends
5. Fine-tune classification models (optional)
6. Add more data sources (optional)

## Support

If issues arise:
1. Check GitHub Actions logs
2. Check Streamlit Cloud logs
3. Check Supabase dashboard for data
4. Run pipeline locally: `python -m macrosentry run`
