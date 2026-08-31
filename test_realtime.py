#!/usr/bin/env python3
"""Diagnostic script to test real-time data sources."""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

print("=" * 80)
print("MacroSentry Real-Time Diagnostic")
print("=" * 80)

# Test 1: Environment variables
print("\nChecking environment variables...")
env_vars = {
    "NEWSAPI_KEY": os.getenv("NEWSAPI_KEY"),
    "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN"),
    "TWITTER_ACCOUNTS": os.getenv("TWITTER_ACCOUNTS"),
    "SUPABASE_URL": os.getenv("SUPABASE_URL"),
}

for key, value in env_vars.items():
    if value:
        print(f"  [OK] {key}: {'***' + value[-10:] if len(str(value)) > 10 else value}")
    else:
        print(f"  [ERROR] {key}: NOT SET")

# Test 2: NewsAPI
print("\nTesting NewsAPI...")
try:
    from src.macrosentry.ingestion import NewsAggregator
    news = NewsAggregator()
    articles = news.fetch_news(keywords=["Fed"])
    print(f"  [OK] NewsAPI working! Fetched {len(articles)} articles")
    for article in articles[:3]:
        print(f"     - {article.headline[:60]}")
except Exception as e:
    print(f"  [ERROR] NewsAPI failed: {e}")

# Test 3: Twitter
print("\nTesting Twitter/X API...")
try:
    from src.macrosentry.twitter_client import TwitterClient
    twitter = TwitterClient()
    tweets = twitter.get_recent_tweets(hours=1)
    print(f"  [OK] Twitter working! Fetched {len(tweets)} tweets")
    for tweet in tweets[:3]:
        print(f"     - @{tweet['author']}: {tweet['text'][:60]}")
except Exception as e:
    print(f"  [ERROR] Twitter failed: {e}")

# Test 4: Supabase Connection
print("\nTesting Supabase...")
try:
    from src.macrosentry.storage import StorageManager
    storage = StorageManager()
    data = storage.get_dashboard_data()
    print(f"  [OK] Supabase connected!")
    print(f"     - Events in DB: {data['accuracy']['events_processed']}")
    print(f"     - Recent events: {len(data['recent_events'])}")
    print(f"     - Accuracy: {data['accuracy']['accuracy']:.1%}")
except Exception as e:
    print(f"  [ERROR] Supabase failed: {e}")

# Test 5: Full Pipeline
print("\nTesting full pipeline...")
try:
    from src.macrosentry.pipeline import MacroSentryPipeline
    pipeline = MacroSentryPipeline()
    print("  [RUNNING] Running pipeline (this may take 30 seconds)...")
    result = pipeline.run()
    print(f"  [OK] Pipeline completed!")
    print(f"     - Events processed: {result['events_processed']}")
    print(f"     - Accuracy: {result['accuracy']:.1%}")
    print(f"     - Errors: {len(result['errors'])}")
    if result['errors']:
        print(f"     - Error details: {result['errors'][0]}")
except Exception as e:
    print(f"  [ERROR] Pipeline failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Diagnostic complete!")
print("=" * 80)
