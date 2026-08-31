# MacroSentry — Claude Code build prompt (from scratch)

Paste the section below into Claude Code as your first message in a new
session, inside your empty `macrosentry` folder. This is self-contained —
don't attach any pre-built files or zips. Let Claude Code design the
folder structure, write every file, and make its own implementation
decisions within the constraints given.

Work through it in the numbered phases at the bottom, one phase per
message, reviewing what it builds before moving to the next phase.

---

## Paste this first — project brief

I want to build a project called **MacroSentry** from scratch. Read this
whole brief, then propose a folder structure and confirm your
understanding before writing any code.

### What it does

An autonomous pipeline that:
1. Watches Federal Reserve statements/speeches, the economic calendar,
   and market news relevant to CME, CBOT, and COMEX futures (gold,
   silver, 10-year notes, corn, soybeans, S&P 500 futures).
2. Classifies each event as **hawkish / dovish / neutral** and
   **low / medium / high impact**.
3. Grounds each classification using RAG — retrieving similar historical
   Fed language from a vector store before classifying, so the
   classification is contextual, not just reading one headline in
   isolation.
4. Checks its own prediction against reality: pulls the relevant
   future's price movement in the 30 minutes after the event and scores
   whether the predicted direction matched what price actually did.
   This running accuracy score is the project's core "wow factor" — a
   self-evaluating feedback loop, not just a one-shot classifier.
5. Publishes results to a public, login-free dashboard.

### Why these Hugging Face task types

Use the Hugging Face Inference API (free tier) for:
- **Zero-shot classification** — for both the hawkish/dovish/neutral
  call and the impact tier call, since I have no labeled training data
  and zero budget for fine-tuning.
- **Token classification (NER)** — to extract entities from headlines
  (e.g. "Fed," "CPI," "gold," "10-year yield") and route each event to
  the correct futures ticker.
- **Summarization** — to compress a long Fed statement or news article
  into a one-sentence "why" for the dashboard.

Pick specific free models for each of these yourself and tell me which
ones and why (e.g. something in the bart-mnli family for zero-shot is a
reasonable default, but confirm current free-tier availability).

### Hard constraints — do not violate these

- **$0 budget.** Every API, model, database, and hosting service must be
  free tier. Call this out explicitly anywhere a paid tier might be
  tempting.
- **I'm on a low-end PC.** Do not run any LLM or classification model
  locally. The only thing that should run locally/on my machine is tiny
  CPU-friendly embedding generation (e.g. a small sentence-transformers
  model) — everything else goes through hosted free APIs.
- **Scheduled compute must run in the cloud, not on my machine.** Use
  GitHub Actions on a cron schedule to run the ingestion/classification
  pipeline, since I can't leave my PC running.
- **Storage must be a free hosted database** (e.g. Supabase free tier)
  that both the GitHub Action and the public dashboard can read/write,
  so the dashboard never depends on my local machine being on.
- **The final deployment must be a public URL with no login and no
  pricing page.** Visiting the site goes straight to the live dashboard.

### Production-grade requirements

This needs to actually demonstrate AI engineering depth, not just chain
API calls. Make sure the build includes:
- **RAG**: a real vector store seeded with historical FOMC statement
  text, queried before every classification call.
- **Agent/graph orchestration**: use LangGraph to structure the pipeline
  as a graph of nodes (ingest → extract entities → retrieve context →
  classify → summarize → check price → self-evaluate), not a flat
  script.
- **Evaluation loop**: the self-eval step described above, with results
  logged so accuracy can be tracked over time, not just printed once.
- **Observability**: structured logging on every node (inputs, outputs,
  duration, errors) so a run can be debugged after the fact.
- **Cost/latency awareness**: batch or rate-limit API calls sensibly
  given free-tier limits, and note anywhere latency could become a
  problem at higher event volume.

### Dashboard requirements

- Dark, minimal, professional look — in the spirit of modern SaaS
  market-data dashboards, but an original design, not copying anyone's
  branding or layout pixel-for-pixel.
- No login screen, no pricing section, no sidebar nav clutter — landing
  on the URL shows the dashboard immediately.
- Show: a "today's overall bias" summary, a "self-eval accuracy" stat,
  and a live feed of recent events each showing headline, bias label,
  impact tier (color-coded), and the one-line "why."
- Use Streamlit unless you think something else free and equally fast
  to build is clearly better — if so, tell me why before switching.

### What I want from you right now

Don't write code yet. First:
1. Propose a clean folder structure for this project.
2. List the exact free tools/services/accounts I need to sign up for
   before you can build (and what each one is for).
3. Propose a phase-by-phase build order (ingestion first, then RAG,
   then classification, then the eval loop, then storage + scheduling,
   then the dashboard, then observability) so we can build and test one
   working piece at a time instead of everything at once.

Wait for my confirmation on the structure and account list before
starting Phase 1.

---

## How to run the phases

After Claude Code responds with its proposed structure and account
list, reply with:

> Looks good, let's start Phase 1: [paste the phase name it gave you].
> Build it, then write a small test so I can confirm it's pulling real
> data before we move on.

Repeat for each phase it proposed. After each phase:
1. Review the code it wrote.
2. Run the test it created.
3. `git add . && git commit -m "phase N: <name>"` before starting the
   next phase.

This keeps every step reviewable and reversible instead of getting one
giant untested generation at the end.
