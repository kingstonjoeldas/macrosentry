"""Configuration and constants."""
import os
from dataclasses import dataclass

@dataclass
class Config:
    """Environment and API configuration."""
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY", "")
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    TWITTER_ACCOUNTS: str = os.getenv("TWITTER_ACCOUNTS", "@mrkt_ai,@fed_watchers,@cmegroup")

    # Hugging Face models (free tier, no auth required)
    ZS_MODEL = "facebook/bart-large-mnli"  # Zero-shot classification
    NER_MODEL = "dslim/bert-base-NER"  # Named entity recognition
    SUMMARIZE_MODEL = "facebook/bart-large-cnn"  # Summarization

    # Assets
    TICKERS = {
        "gold": "XAUUSD",
        "silver": "XAGUSD",
        "10y_notes": "ZN",
        "corn": "ZC",
        "soybeans": "ZS",
        "sp500": "ES",
    }

    # LLM settings
    EVAL_WINDOW_MINUTES = 30  # Check price movement 30min after event
    MAX_RETRIES = 3
    BATCH_SIZE = 5  # Rate limit awareness

config = Config()
