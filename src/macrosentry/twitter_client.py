"""Phase 7: Twitter/X integration for real-time market commentary."""
import logging
from typing import List, Dict
import tweepy
from datetime import datetime, timedelta

from .config import config

logger = logging.getLogger(__name__)


class TwitterClient:
    """Fetch and parse tweets from monitored accounts."""

    def __init__(self):
        self.bearer_token = config.TWITTER_BEARER_TOKEN
        self.accounts = [acc.strip().lstrip("@") for acc in config.TWITTER_ACCOUNTS.split(",")]
        self.client = None

        if self.bearer_token:
            try:
                self.client = tweepy.Client(bearer_token=self.bearer_token)
                logger.info(f"Initialized Twitter client, monitoring {len(self.accounts)} accounts")
            except Exception as e:
                logger.warning(f"Failed to initialize Twitter client: {e}")

    def get_recent_tweets(self, hours: int = 1) -> List[Dict]:
        """Fetch recent tweets from monitored accounts."""
        if not self.client:
            logger.warning("Twitter client not initialized")
            return []

        tweets = []
        start_time = datetime.utcnow() - timedelta(hours=hours)

        for account in self.accounts:
            try:
                # Search for tweets from this account in the last hour
                query = f"from:{account} -is:retweet lang:en"
                response = self.client.search_recent_tweets(
                    query=query,
                    start_time=start_time,
                    max_results=10,
                    tweet_fields=["created_at", "public_metrics"],
                    expansions=["author_id"],
                    user_fields=["username"],
                )

                if response.data:
                    for tweet in response.data:
                        tweets.append({
                            "id": str(tweet.id),
                            "text": tweet.text,
                            "author": account,
                            "created_at": tweet.created_at.isoformat(),
                            "likes": tweet.public_metrics.get("like_count", 0),
                            "retweets": tweet.public_metrics.get("retweet_count", 0),
                            "source": "twitter",
                            "url": f"https://twitter.com/{account}/status/{tweet.id}",
                        })
                        logger.info(f"Fetched tweet from @{account}: {tweet.text[:80]}...")

            except Exception as e:
                logger.warning(f"Failed to fetch tweets from @{account}: {e}")

        return tweets

    def post_tweet(self, text: str) -> bool:
        """Post a tweet with market analysis results."""
        if not self.client:
            logger.warning("Twitter client not initialized")
            return False

        try:
            # Note: posting requires elevated access, not available on free tier
            # This is a placeholder for future implementation
            logger.info(f"Would post: {text}")
            return False
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            return False


# Helper function
def create_tweet_from_event(event: Dict) -> str:
    """Format an event as a tweet."""
    bias_emoji = {"hawkish": "🔴", "dovish": "🔵", "neutral": "⚪"}.get(event.get("bias"), "❓")
    impact = event.get("impact", "low").upper()

    return (
        f"{bias_emoji} {event.get('bias', 'NEUTRAL').upper()}\n"
        f"Impact: {impact}\n"
        f"{event.get('headline', '')[:100]}\n"
        f"#Fed #Markets"
    )
