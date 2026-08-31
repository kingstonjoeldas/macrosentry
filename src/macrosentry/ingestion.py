"""Phase 1: Fetch Fed statements, speeches, and economic news."""
import logging
import requests
from datetime import datetime, timedelta
from typing import Optional
from bs4 import BeautifulSoup
import json

from .schemas import RawEvent
from .config import config

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
                        id=f"fed_{len(events)}",
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
                        id=f"speech_{len(events)}",
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
                id=f"econ_{len(events)}",
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
    """Fetch market-relevant news (simplified mock)."""

    def fetch_news(self, keywords: list[str] = None) -> list[RawEvent]:
        """Fetch recent market news."""
        if keywords is None:
            keywords = ["Fed", "Federal Reserve", "interest rates", "gold", "inflation"]

        events = []

        # Mock news (in production: use NewsAPI free tier)
        mock_news = [
            "Fed signals cautious approach to rate cuts",
            "Gold surges as inflation concerns rise",
            "10-year yield drops amid economic slowdown",
            "Market awaits Powell speech on policy outlook",
        ]

        for i, headline in enumerate(mock_news):
            events.append(RawEvent(
                id=f"news_{i}",
                source="news",
                headline=headline,
                body=headline,
                published_at=datetime.now(),
                url="",
                tickers=[]
            ))

        logger.info(f"Fetched {len(events)} news items")
        return events


class Ingester:
    """Main ingestion orchestrator."""

    def __init__(self):
        self.fed_fetcher = FedStatementFetcher()
        self.calendar_fetcher = EconomicCalendarFetcher()
        self.news_fetcher = NewsAggregator()

    def ingest_all(self) -> list[RawEvent]:
        """Fetch all event sources."""
        events = []
        events.extend(self.fed_fetcher.fetch_recent_statements())
        events.extend(self.fed_fetcher.fetch_speeches())
        events.extend(self.calendar_fetcher.fetch_calendar())
        events.extend(self.news_fetcher.fetch_news())

        logger.info(f"Total events ingested: {len(events)}")
        return events


# CLI for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ingester = Ingester()
    events = ingester.ingest_all()
    for event in events:
        print(f"[{event.source}] {event.headline}")
