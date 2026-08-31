"""Phase 5: Storage - Supabase integration for database."""
import logging
from datetime import datetime
from typing import Optional, List
import json

from .types import EvaluatedEvent, PipelineRun
from .config import config

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabase database client (mock for now, real implementation uses supabase library)."""

    def __init__(self, url: str = "", key: str = ""):
        self.url = url or config.SUPABASE_URL
        self.key = key or config.SUPABASE_KEY

        # In production: use real supabase client
        # from supabase import create_client
        # self.client = create_client(url, key)

        # For demo: in-memory storage
        self.events = []
        self.runs = []
        self.accuracy_history = []

        logger.info("Initialized Supabase client (mock mode)")

    def create_tables(self):
        """
        Create necessary tables if they don't exist.
        In production: would run actual SQL schema.
        """
        schema = """
        -- Events table
        CREATE TABLE IF NOT EXISTS events (
            id UUID PRIMARY KEY,
            source TEXT,
            headline TEXT,
            body TEXT,
            published_at TIMESTAMP,
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
            evaluated_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Pipeline runs table
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id UUID PRIMARY KEY,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            events_processed INT,
            errors JSONB,
            accuracy FLOAT,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Accuracy history
        CREATE TABLE IF NOT EXISTS accuracy_history (
            id UUID PRIMARY KEY,
            run_id UUID REFERENCES pipeline_runs(id),
            accuracy FLOAT,
            timestamp TIMESTAMP DEFAULT NOW()
        );
        """
        logger.info("Schema created (mock)")

    def insert_event(self, evaluated_event: EvaluatedEvent) -> bool:
        """Insert a classified and evaluated event."""
        try:
            event_record = {
                "id": evaluated_event.classified.event.id,
                "source": evaluated_event.classified.event.source,
                "headline": evaluated_event.classified.event.headline,
                "body": evaluated_event.classified.event.body[:500],
                "published_at": evaluated_event.classified.event.published_at.isoformat(),
                "url": evaluated_event.classified.event.url,
                "bias": evaluated_event.classified.bias,
                "bias_confidence": evaluated_event.classified.bias_confidence,
                "impact": evaluated_event.classified.impact,
                "impact_confidence": evaluated_event.classified.impact_confidence,
                "summary": evaluated_event.classified.summary,
                "entities": json.dumps(evaluated_event.classified.entities),
                "price_direction": evaluated_event.price_direction,
                "price_pct_change": evaluated_event.price_pct_change,
                "prediction_correct": evaluated_event.prediction_correct,
                "evaluated_at": evaluated_event.evaluated_at.isoformat(),
            }
            self.events.append(event_record)
            logger.info(f"Inserted event: {evaluated_event.classified.event.headline[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Error inserting event: {e}")
            return False

    def insert_run(self, run: PipelineRun) -> bool:
        """Insert a pipeline run record."""
        try:
            run_record = {
                "id": run.run_id,
                "started_at": run.started_at.isoformat(),
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                "events_processed": run.events_processed,
                "errors": json.dumps(run.errors),
                "accuracy": run.accuracy,
            }
            self.runs.append(run_record)
            logger.info(f"Inserted run: {run.run_id}")
            return True

        except Exception as e:
            logger.error(f"Error inserting run: {e}")
            return False

    def get_recent_events(self, limit: int = 50) -> List[dict]:
        """Get recent classified events for dashboard."""
        # Sort by published_at desc, return top N
        sorted_events = sorted(
            self.events,
            key=lambda x: x["published_at"],
            reverse=True
        )
        return sorted_events[:limit]

    def get_accuracy_stats(self) -> dict:
        """Get accuracy statistics."""
        if not self.runs:
            return {"accuracy": 0.0, "total_runs": 0, "events_processed": 0}

        accuracies = [r["accuracy"] for r in self.runs if r["accuracy"] is not None]
        total_events = sum(r["events_processed"] for r in self.runs)

        return {
            "accuracy": sum(accuracies) / len(accuracies) if accuracies else 0.0,
            "total_runs": len(self.runs),
            "events_processed": total_events,
        }

    def get_bias_summary(self, hours: int = 24) -> dict:
        """Get bias summary for dashboard (hawkish/dovish/neutral count)."""
        hawkish = sum(1 for e in self.events if e["bias"] == "hawkish")
        dovish = sum(1 for e in self.events if e["bias"] == "dovish")
        neutral = sum(1 for e in self.events if e["bias"] == "neutral")

        total = hawkish + dovish + neutral
        if total == 0:
            return {"hawkish": 0, "dovish": 0, "neutral": 0, "bias": "neutral"}

        # Overall bias: if dovish > hawkish, dovish; vice versa; else neutral
        if dovish > hawkish * 1.2:
            bias = "dovish"
        elif hawkish > dovish * 1.2:
            bias = "hawkish"
        else:
            bias = "neutral"

        return {
            "hawkish": hawkish,
            "dovish": dovish,
            "neutral": neutral,
            "bias": bias,
        }


class StorageManager:
    """Main storage orchestrator."""

    def __init__(self):
        self.db = SupabaseClient()
        self.db.create_tables()

    def save_pipeline_run(self, run: PipelineRun, evaluated_events: list[EvaluatedEvent]):
        """Save complete pipeline run."""
        # Insert each event
        for event in evaluated_events:
            self.db.insert_event(event)

        # Update run with stats
        run.events_processed = len(evaluated_events)
        if evaluated_events:
            from .evaluation import Evaluator
            evaluator = Evaluator()
            run.accuracy = evaluator.compute_accuracy(evaluated_events)

        run.completed_at = datetime.now()

        # Insert run
        self.db.insert_run(run)

        logger.info(f"Saved pipeline run with {len(evaluated_events)} events")

    def get_dashboard_data(self) -> dict:
        """Get all data needed for dashboard."""
        recent_events = self.db.get_recent_events(limit=20)
        accuracy_stats = self.db.get_accuracy_stats()
        bias_summary = self.db.get_bias_summary()

        return {
            "recent_events": recent_events,
            "accuracy": accuracy_stats,
            "bias_summary": bias_summary,
            "last_updated": datetime.now().isoformat(),
        }


# CLI for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    from .evaluation import Evaluator
    from .classification import Classifier
    from .ingestion import Ingester
    import uuid

    # Build pipeline
    ingester = Ingester()
    classifier = Classifier()
    evaluator = Evaluator()
    storage = StorageManager()

    # Run pipeline
    run = PipelineRun(
        run_id=str(uuid.uuid4()),
        started_at=datetime.now()
    )

    events = ingester.ingest_all()[:3]
    classified = classifier.classify_batch(events)
    evaluated = evaluator.evaluate_batch(classified)

    # Save
    storage.save_pipeline_run(run, evaluated)

    # Get dashboard data
    dashboard_data = storage.get_dashboard_data()
    print(f"\nDashboard Data:")
    print(f"  Accuracy: {dashboard_data['accuracy']['accuracy']:.1%}")
    print(f"  Bias: {dashboard_data['bias_summary']['bias']}")
    print(f"  Recent Events: {len(dashboard_data['recent_events'])}")
