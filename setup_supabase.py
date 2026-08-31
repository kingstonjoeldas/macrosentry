#!/usr/bin/env python3
"""Setup Supabase tables for MacroSentry."""
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")
    exit(1)

from supabase import create_client

client = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQL to create tables
create_tables_sql = """
-- Events table
CREATE TABLE IF NOT EXISTS public.events (
    id UUID PRIMARY KEY,
    source TEXT,
    headline TEXT,
    body TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    url TEXT,
    bias TEXT,
    bias_confidence FLOAT,
    impact TEXT,
    impact_confidence FLOAT,
    summary TEXT,
    entities JSONB,
    price_direction TEXT,
    price_pct_change FLOAT,
    prediction_correct BOOLEAN,
    evaluated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pipeline runs table
CREATE TABLE IF NOT EXISTS public.pipeline_runs (
    id UUID PRIMARY KEY,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    events_processed INT,
    errors JSONB,
    accuracy FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Accuracy history
CREATE TABLE IF NOT EXISTS public.accuracy_history (
    id UUID PRIMARY KEY,
    run_id UUID REFERENCES public.pipeline_runs(id),
    accuracy FLOAT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security (optional)
ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pipeline_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.accuracy_history ENABLE ROW LEVEL SECURITY;

-- Allow public read access (no login required)
CREATE POLICY "Enable read access for all users" ON public.events
  FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON public.pipeline_runs
  FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON public.accuracy_history
  FOR SELECT USING (true);

-- Allow insert from GitHub Actions (authenticated)
CREATE POLICY "Enable insert for authenticated users" ON public.events
  FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable insert for authenticated users" ON public.pipeline_runs
  FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable insert for authenticated users" ON public.accuracy_history
  FOR INSERT WITH CHECK (true);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_events_published_at ON public.events(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_created_at ON public.pipeline_runs(created_at DESC);
"""

try:
    # Execute SQL via RPC (if supported) or provide manual instructions
    response = client.rpc("exec_sql", {"sql": create_tables_sql}).execute()
    print("✅ Tables created successfully!")
except Exception as e:
    print(f"⚠️  Could not create tables via API: {e}")
    print("\n📋 Run this SQL manually in Supabase Console (SQL Editor):\n")
    print(create_tables_sql)
    print("\n1. Go to: https://app.supabase.com")
    print("2. Select your project")
    print("3. Go to SQL Editor")
    print("4. Click 'New Query'")
    print("5. Paste the SQL above and click 'Run'")
    print("\n✅ After running, your dashboard will work!")
