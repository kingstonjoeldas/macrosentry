"""Phase 4: Self-evaluation - Check predictions against actual price movements."""
import logging
from datetime import datetime, timedelta
from typing import Optional
import random

from .schemas import ClassifiedEvent, EvaluatedEvent
from .config import config

logger = logging.getLogger(__name__)

class PriceFetcher:
    """Fetch futures prices (mock implementation)."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or config.ALPHA_VANTAGE_API_KEY
        # In production: use Alpha Vantage free tier or similar

    def get_price_movement(
        self,
        ticker: str,
        start_time: datetime,
        duration_minutes: int = 30
    ) -> Optional[dict]:
        """
        Get price movement in time window after event.
        Mock: simulates realistic price movements.
        """
        try:
            # In production: fetch from Alpha Vantage, FRED, or CME data
            # For now: mock realistic movement
            base_price = 100.0 + random.uniform(-10, 10)
            price_change = random.uniform(-2.0, 2.0)  # percent change
            end_price = base_price * (1 + price_change / 100)

            return {
                "ticker": ticker,
                "start_time": start_time,
                "start_price": base_price,
                "end_price": end_price,
                "pct_change": price_change,
                "direction": "up" if price_change > 0.1 else ("down" if price_change < -0.1 else "flat"),
                "duration_minutes": duration_minutes,
                "data_source": "mock"
            }

        except Exception as e:
            logger.error(f"Error fetching price for {ticker}: {e}")
            return None

    def get_movement_for_event(
        self,
        tickers: list[str],
        event_time: datetime
    ) -> dict[str, dict]:
        """Get price movement for all relevant tickers."""
        movements = {}
        for ticker in tickers:
            movement = self.get_price_movement(
                ticker,
                event_time,
                duration_minutes=config.EVAL_WINDOW_MINUTES
            )
            if movement:
                movements[ticker] = movement
        return movements


class Evaluator:
    """Self-evaluation: check prediction accuracy."""

    def __init__(self):
        self.price_fetcher = PriceFetcher()

    def predict_price_direction(self, classified: ClassifiedEvent) -> str:
        """
        Predict price direction based on classified bias.
        Hawkish → stronger dollar, gold/commodity down
        Dovish → weaker dollar, gold/commodity up
        Neutral → flat
        """
        if classified.bias == "dovish":
            return "up"  # Risk assets up, gold up, USD down
        elif classified.bias == "hawkish":
            return "down"  # Risk assets down, gold down, USD up
        else:
            return "flat"

    def evaluate_event(self, classified: ClassifiedEvent) -> EvaluatedEvent:
        """
        Full evaluation: fetch price data, compare prediction vs reality.
        """
        try:
            # Determine tickers relevant to this event
            tickers_to_check = []
            text_lower = classified.event.headline.lower()

            for keyword, ticker in config.TICKERS.items():
                if keyword.lower() in text_lower:
                    tickers_to_check.append(ticker)

            # Default: check all if no specific mention
            if not tickers_to_check:
                tickers_to_check = list(config.TICKERS.values())[:3]

            # Fetch actual price movements
            price_movements = self.price_fetcher.get_movement_for_event(
                tickers_to_check,
                classified.event.published_at
            )

            # Predict direction
            predicted_direction = self.predict_price_direction(classified)

            # Evaluate: did actual match prediction?
            if price_movements:
                # Take first ticker's movement as representative
                first_movement = next(iter(price_movements.values()))
                actual_direction = first_movement["direction"]
                price_pct_change = first_movement["pct_change"]

                # Score: prediction correct if both are same
                prediction_correct = (predicted_direction == actual_direction)

            else:
                actual_direction = None
                price_pct_change = None
                prediction_correct = None

            evaluated = EvaluatedEvent(
                classified=classified,
                price_direction=actual_direction,
                price_pct_change=price_pct_change,
                prediction_correct=prediction_correct,
                evaluated_at=datetime.now()
            )

            logger.info(
                f"Evaluated: {classified.event.headline[:50]}... "
                f"Predicted {predicted_direction}, Actual {actual_direction} "
                f"({prediction_correct})"
            )

            return evaluated

        except Exception as e:
            logger.error(f"Error evaluating event: {e}")
            return EvaluatedEvent(
                classified=classified,
                price_direction=None,
                price_pct_change=None,
                prediction_correct=None,
                evaluated_at=datetime.now()
            )

    def evaluate_batch(self, classified: list[ClassifiedEvent]) -> list[EvaluatedEvent]:
        """Evaluate multiple events."""
        evaluated = []
        for ce in classified:
            evaluated.append(self.evaluate_event(ce))
        logger.info(f"Evaluated {len(evaluated)} events")
        return evaluated

    def compute_accuracy(self, evaluated: list[EvaluatedEvent]) -> float:
        """Compute overall accuracy from evaluated events."""
        if not evaluated:
            return 0.0

        correct = sum(1 for e in evaluated if e.prediction_correct is True)
        total = sum(1 for e in evaluated if e.prediction_correct is not None)

        accuracy = correct / total if total > 0 else 0.0
        logger.info(f"Accuracy: {correct}/{total} = {accuracy:.1%}")
        return accuracy


# CLI for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    from .classification import Classifier
    from .ingestion import Ingester

    ingester = Ingester()
    classifier = Classifier()
    evaluator = Evaluator()

    events = ingester.ingest_all()
    classified = classifier.classify_batch(events[:3])
    evaluated = evaluator.evaluate_batch(classified)

    for ee in evaluated:
        print(f"\n{ee.classified.event.headline}")
        print(f"  Predicted: {ee.classified.bias} → {Evaluator().predict_price_direction(ee.classified)}")
        print(f"  Actual: {ee.price_direction} ({ee.price_pct_change:.2f}%)")
        print(f"  Correct: {ee.prediction_correct}")

    accuracy = evaluator.compute_accuracy(evaluated)
    print(f"\nOverall Accuracy: {accuracy:.1%}")
