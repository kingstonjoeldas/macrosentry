"""Phase 7: Observability - Structured logging and monitoring."""
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

class StructuredLogger:
    """Structured logging with JSON output for debugging."""

    def __init__(self, log_dir: str = "data/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        self.logger = logging.getLogger("macrosentry")

    def log_event(
        self,
        event_type: str,
        message: str,
        metadata: Optional[dict] = None,
        level: str = "info"
    ):
        """Log structured event."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message,
            "metadata": metadata or {},
        }

        # Write to file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Also log to console
        log_func = getattr(self.logger, level, self.logger.info)
        log_func(f"[{event_type}] {message}")

    def log_ingestion_start(self, sources: list[str]):
        """Log pipeline ingestion phase."""
        self.log_event(
            "ingestion_start",
            "Started ingestion phase",
            {"sources": sources}
        )

    def log_ingestion_complete(self, count: int, duration_sec: float):
        """Log ingestion completion."""
        self.log_event(
            "ingestion_complete",
            f"Ingested {count} events",
            {"event_count": count, "duration_sec": duration_sec}
        )

    def log_classification_start(self, event_count: int):
        """Log classification phase start."""
        self.log_event(
            "classification_start",
            f"Starting classification of {event_count} events",
            {"event_count": event_count}
        )

    def log_classification_event(
        self,
        event_id: str,
        headline: str,
        bias: str,
        impact: str,
        confidence: float
    ):
        """Log individual event classification."""
        self.log_event(
            "classification_event",
            f"Classified: {headline[:50]}...",
            {
                "event_id": event_id,
                "bias": bias,
                "impact": impact,
                "confidence": confidence
            }
        )

    def log_evaluation_event(
        self,
        event_id: str,
        headline: str,
        prediction: str,
        actual: str,
        correct: bool
    ):
        """Log individual event evaluation."""
        self.log_event(
            "evaluation_event",
            f"Evaluated: {headline[:50]}...",
            {
                "event_id": event_id,
                "prediction": prediction,
                "actual": actual,
                "correct": correct
            }
        )

    def log_accuracy_result(self, accuracy: float, total: int, correct: int):
        """Log accuracy result."""
        self.log_event(
            "accuracy_result",
            f"Accuracy: {correct}/{total} = {accuracy:.1%}",
            {"accuracy": accuracy, "total": total, "correct": correct}
        )

    def log_error(self, error_type: str, message: str, metadata: Optional[dict] = None):
        """Log error."""
        self.log_event(
            error_type,
            message,
            metadata,
            level="error"
        )

    def log_pipeline_complete(
        self,
        duration_sec: float,
        events_processed: int,
        accuracy: float,
        errors: list[str]
    ):
        """Log complete pipeline run."""
        self.log_event(
            "pipeline_complete",
            f"Pipeline completed: {events_processed} events, {accuracy:.1%} accuracy",
            {
                "duration_sec": duration_sec,
                "events_processed": events_processed,
                "accuracy": accuracy,
                "error_count": len(errors),
                "errors": errors[:10]  # First 10 errors only
            }
        )

    def get_latest_logs(self, limit: int = 50) -> list[dict]:
        """Get latest log entries."""
        if not self.log_file.exists():
            return []

        entries = []
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

        return entries[-limit:]


class MetricsCollector:
    """Collect and track metrics."""

    def __init__(self):
        self.metrics = {}
        self.start_time = None

    def start_timer(self, name: str):
        """Start timing a section."""
        if not hasattr(self, "_timers"):
            self._timers = {}
        self._timers[name] = datetime.now()

    def end_timer(self, name: str) -> float:
        """End timing and return duration in seconds."""
        if not hasattr(self, "_timers") or name not in self._timers:
            return 0.0

        duration = (datetime.now() - self._timers[name]).total_seconds()
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(duration)

        return duration

    def record_metric(self, name: str, value: float):
        """Record a metric value."""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)

    def get_summary(self) -> dict:
        """Get metrics summary."""
        summary = {}
        for name, values in self.metrics.items():
            if values:
                summary[name] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "count": len(values),
                }
        return summary


# Configure root logger
def configure_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# CLI for testing
if __name__ == "__main__":
    configure_logging()
    logger = StructuredLogger()

    logger.log_ingestion_start(["fed_statement", "fed_speech", "econ_calendar"])
    logger.log_ingestion_complete(25, 3.5)

    logger.log_classification_start(25)
    logger.log_classification_event("evt_1", "Fed raises rates", "hawkish", "high", 0.95)

    logger.log_evaluation_event("evt_1", "Fed raises rates", "down", "down", True)
    logger.log_accuracy_result(0.72, 25, 18)

    logger.log_pipeline_complete(45.2, 25, 0.72, [])

    print("\nRecent logs:")
    for entry in logger.get_latest_logs(5):
        print(f"  {entry['timestamp']} [{entry['event_type']}] {entry['message']}")
