"""Phase 1: Fetch Fed statements, speeches, and economic news."""
import logging
import requests
from datetime import datetime, timedelta
from typing import Optional
from bs4 import BeautifulSoup
import json
import uuid

from .schemas import RawEvent
from .config import config
from .twitter_client import TwitterClient

logger = logging.getLogger(__name__)

class FedStatementFetcher:
    """Fetch recent FOMC statements and speeches from Federal Reserve."""

    def __init__(self):
        self.base_url = "https://www.federalreserve.gov"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "MacroSentry/1.0 (AI event monitoring)"
        })

    def fetch_recent_statements(self, days: int = 7) -> list[RawEvent]:
        """Fetch recent FOMC statements (last N days)."""
        events = []
        try:
            # Fetch calendar of events from Federal Reserve
            url = f"{self.base_url}/newsevents/index.htm"
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.content, "html.parser")

            # Find recent FOMC minutes/statements (simplified extraction)
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                text = link.get_text(strip=True)

                if any(x in text.lower() for x in ["fomc", "minutes", "statement"]):
                    # Create event entry
                    event = RawEvent(
                        id=str(uuid.uuid4()),  # Generate proper UUID
                        source="fed_statement",
                        headline=text[:100],
                        body="",  # Would fetch full text in production
                        published_at=datetime.now(),
                        url=f"{self.base_url}{href}" if href.startswith("/") else href,
                        tickers=[]
                    )
                    events.append(event)

            logger.info(f"Fetched {len(events)} Fed statements")
            return events[:5]  # Rate limit: return top 5

        except Exception as e:
            logger.error(f"Error fetching Fed statements: {e}")
            return []

    def fetch_speeches(self, days: int = 7) -> list[RawEvent]:
        """Fetch recent Fed official speeches."""
        try:
            url = f"{self.base_url}/newsevents/speech/index.htm"
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.content, "html.parser")
            events = []

            for item in soup.find_all("li")[:5]:  # Top 5 speeches
                link = item.find("a")
                if link:
                    event = RawEvent(
                        id=str(uuid.uuid4()),  # Generate proper UUID
                        source="fed_speech",
                        headline=link.get_text(strip=True)[:100],
                        body="",
                        published_at=datetime.now(),
                        url=f"{self.base_url}{link.get('href', '')}" if link.get('href', '').startswith("/") else link.get('href', ''),
                        tickers=[]
                    )
                    events.append(event)

            logger.info(f"Fetched {len(events)} Fed speeches")
            return events

        except Exception as e:
            logger.error(f"Error fetching Fed speeches: {e}")
            return []


class EconomicCalendarFetcher:
    """Fetch economic calendar events (simplified mock)."""

    def fetch_calendar(self, days: int = 7) -> list[RawEvent]:
        """Fetch upcoming economic calendar events."""
        events = []

        # Mock economic calendar (in production: use Fred API, trading calendars)
        mock_events = [
            ("CPI Release", "Consumer Price Index", "high"),
            ("Jobs Report", "Non-farm payrolls", "high"),
            ("Fed Rate Decision", "Policy decision", "high"),
            ("GDP Growth", "Quarterly GDP", "medium"),
        ]

        for headline, body, impact in mock_events:
            events.append(RawEvent(
                id=str(uuid.uuid4()),  # Generate proper UUID
                source="econ_calendar",
                headline=headline,
                body=body,
                published_at=datetime.now(),
                url="",
                tickers=[]
            ))

        logger.info(f"Fetched {len(events)} economic calendar events")
        return events


class NewsAggregator:
    """Fetch real market-relevant news from NewsAPI."""

    def __init__(self):
        self.api_key = config.NEWSAPI_KEY
        self.base_url = "https://newsapi.org/v2/everything"
        self.session = requests.Session()

    def fetch_news(self, keywords: list[str] = None) -> list[RawEvent]:
        """Fetch recent market news from NewsAPI."""
        if keywords is None:
            keywords = ["Fed", "Federal Reserve", "interest rates", "gold", "inflation", "market"]

        if not self.api_key:
            logger.warning("NewsAPI key not configured, using mock data")
            return self._mock_news()

        events = []

        for keyword in keywords[:3]:  # Limit to 3 queries to stay within free tier
            try:
                params = {
                    "q": keyword,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "pageSize": 5,
                    "apiKey": self.api_key
                }

                resp = self.session.get(self.base_url, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()

                if data.get("articles"):
                    for article in data.get("articles", [])[:5]:
                        event = RawEvent(
                            id=str(uuid.uuid4()),  # Generate proper UUID
                            source="newsapi",
                            headline=article.get("title", "")[:200],
                            body=article.get("description", "")[:500],
                            published_at=datetime.fromisoformat(
                                article.get("publishedAt", "").replace("Z", "+00:00")
                            ) if article.get("publishedAt") else datetime.now(),
                            url=article.get("url", ""),
                            tickers=[]
                        )
                        events.append(event)
                        logger.info(f"Fetched news: {article.get('title', '')[:80]}...")

            except Exception as e:
                logger.warning(f"Error fetching news for '{keyword}': {e}")

        logger.info(f"Fetched {len(events)} news items from NewsAPI")
        return events[:20]  # Return top 20 articles

    def _mock_news(self) -> list[RawEvent]:
        """Fallback to mock news if API unavailable."""
        mock_news = [
            "Fed signals cautious approach to rate cuts",
            "Gold surges as inflation concerns rise",
            "10-year yield drops amid economic slowdown",
            "Market awaits Powell speech on policy outlook",
        ]

        events = []
        for headline in mock_news:
            events.append(RawEvent(
                id=str(uuid.uuid4()),  # Generate proper UUID
                source="news_mock",
                headline=headline,
                body=headline,
                published_at=datetime.now(),
                url="",
                tickers=[]
            ))

        return events


class Ingester:
    """Main ingestion orchestrator."""

    def __init__(self):
        self.fed_fetcher = FedStatementFetcher()
        self.calendar_fetcher = EconomicCalendarFetcher()
        self.news_fetcher = NewsAggregator()
        self.twitter_client = TwitterClient()

    def ingest_all(self) -> list[RawEvent]:
        """Fetch all event sources (news, Fed, calendar, Twitter)."""
        events = []
        events.extend(self.fed_fetcher.fetch_recent_statements())
        events.extend(self.fed_fetcher.fetch_speeches())
        events.extend(self.calendar_fetcher.fetch_calendar())
        events.extend(self.news_fetcher.fetch_news())
        events.extend(self._ingest_twitter())

        logger.info(f"Total events ingested: {len(events)}")
        return events

    def _ingest_twitter(self) -> list[RawEvent]:
        """Convert Twitter data to RawEvent format."""
        events = []
        tweets = self.twitter_client.get_recent_tweets(hours=1)

        for tweet in tweets:
            event = RawEvent(
                id=str(uuid.uuid4()),  # Generate proper UUID
                source=f"twitter_{tweet['author']}",
                headline=tweet["text"][:200],
                body=tweet["text"],
                published_at=datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00")),
                url=tweet["url"],
                tickers=[]
            )
            events.append(event)

        logger.info(f"Fetched {len(events)} tweets")
        return events


# CLI for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ingester = Ingester()
    events = ingester.ingest_all()
    for event in events:
        print(f"[{event.source}] {event.headline}")
