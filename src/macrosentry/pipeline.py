"""Main pipeline orchestrator."""
import logging
import uuid
from datetime import datetime
from typing import Sequence

from .ingestion import Ingester
from .classification import Classifier
from .evaluation import Evaluator
from .storage import StorageManager
from .observability import StructuredLogger, configure_logging
from .types import PipelineRun, RawEvent, ClassifiedEvent, EvaluatedEvent

configure_logging()
logger = logging.getLogger(__name__)


class PipelineState:
    """Pipeline execution state."""
    def __init__(self):
        self.run_id: str = ""
        self.raw_events: list[RawEvent] = []
        self.classified_events: list[ClassifiedEvent] = []
        self.evaluated_events: list[EvaluatedEvent] = []
        self.errors: list[str] = []
        self.accuracy: float = 0.0


class MacroSentryPipeline:
    """Main pipeline orchestrator."""

    def __init__(self):
        self.ingester = Ingester()
        self.classifier = Classifier()
        self.evaluator = Evaluator()
        self.storage = StorageManager()
        self.structured_logger = StructuredLogger()

    def run(self) -> dict:
        """Execute the complete pipeline."""
        logger.info("Starting MacroSentry pipeline")

        state = PipelineState()
        state.run_id = str(uuid.uuid4())

        # Phase 1: Ingest
        self._node_ingest(state)

        # Phase 2: Classify
        self._node_classify(state)

        # Phase 3: Evaluate
        self._node_evaluate(state)

        # Phase 4: Store
        self._node_store(state)

        logger.info("Pipeline execution completed")
        logger.info(f"Processed: {state.accuracy:.1%} accuracy over {len(state.evaluated_events)} events")

        return {
            "run_id": state.run_id,
            "events_processed": len(state.evaluated_events),
            "accuracy": state.accuracy,
            "errors": state.errors,
            "dashboard_data": self.storage.get_dashboard_data()
        }

    def _node_ingest(self, state: PipelineState):
        """Ingest phase: fetch events."""
        logger.info("Starting ingestion phase")
        self.structured_logger.log_ingestion_start(
            ["fed_statement", "fed_speech", "econ_calendar", "news"]
        )

        try:
            raw_events = self.ingester.ingest_all()
            state.raw_events = raw_events

            self.structured_logger.log_ingestion_complete(
                len(raw_events),
                0.0  # Would track actual duration
            )

            logger.info(f"Ingested {len(raw_events)} events")

        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            state.errors.append(f"Ingestion error: {str(e)}")

    def _node_classify(self, state: PipelineState):
        """Classification phase: classify events."""
        logger.info(f"Starting classification of {len(state.raw_events)} events")
        self.structured_logger.log_classification_start(len(state.raw_events))

        try:
            classified = self.classifier.classify_batch(state.raw_events)
            state.classified_events = classified

            for ce in classified:
                self.structured_logger.log_classification_event(
                    event_id=ce.event.id,
                    headline=ce.event.headline,
                    bias=ce.bias,
                    impact=ce.impact,
                    confidence=ce.bias_confidence
                )

            logger.info(f"Classified {len(classified)} events")

        except Exception as e:
            logger.error(f"Classification failed: {e}")
            state.errors.append(f"Classification error: {str(e)}")

    def _node_evaluate(self, state: PipelineState):
        """Evaluation phase: check predictions against price."""
        logger.info(f"Starting evaluation of {len(state.classified_events)} events")

        try:
            evaluated = self.evaluator.evaluate_batch(state.classified_events)
            state.evaluated_events = evaluated

            for ee in evaluated:
                self.structured_logger.log_evaluation_event(
                    event_id=ee.classified.event.id,
                    headline=ee.classified.event.headline,
                    prediction=self.evaluator.predict_price_direction(ee.classified),
                    actual=ee.price_direction or "unknown",
                    correct=ee.prediction_correct or False
                )

            # Compute accuracy
            accuracy = self.evaluator.compute_accuracy(evaluated)
            state.accuracy = accuracy

            correct = sum(1 for e in evaluated if e.prediction_correct is True)
            total = sum(1 for e in evaluated if e.prediction_correct is not None)
            self.structured_logger.log_accuracy_result(accuracy, total, correct)

            logger.info(f"Evaluated {len(evaluated)} events (accuracy: {accuracy:.1%})")

        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            state.errors.append(f"Evaluation error: {str(e)}")

    def _node_store(self, state: PipelineState):
        """Storage phase: save results to database."""
        logger.info(f"Starting storage of {len(state.evaluated_events)} events")

        try:
            run = PipelineRun(
                run_id=state.run_id,
                started_at=datetime.now(),
                events_processed=len(state.evaluated_events),
                errors=state.errors,
                accuracy=state.accuracy
            )

            self.storage.save_pipeline_run(run, state.evaluated_events)

            self.structured_logger.log_pipeline_complete(
                duration_sec=0.0,  # Would track actual
                events_processed=len(state.evaluated_events),
                accuracy=state.accuracy,
                errors=state.errors
            )

            logger.info(f"Stored {len(state.evaluated_events)} events")

        except Exception as e:
            logger.error(f"Storage failed: {e}")
            state.errors.append(f"Storage error: {str(e)}")


# CLI
if __name__ == "__main__":
    pipeline = MacroSentryPipeline()
    result = pipeline.run()

    print(f"\n{'='*60}")
    print(f"MacroSentry Pipeline Result")
    print(f"{'='*60}")
    print(f"Run ID: {result['run_id']}")
    print(f"Events Processed: {result['events_processed']}")
    print(f"Accuracy: {result['accuracy']:.1%}")
    print(f"Errors: {len(result['errors'])}")

    dashboard = result["dashboard_data"]
    print(f"\nDashboard Summary:")
    print(f"  Overall Bias: {dashboard['bias_summary']['bias'].upper()}")
    print(f"    Hawkish: {dashboard['bias_summary']['hawkish']}")
    print(f"    Dovish: {dashboard['bias_summary']['dovish']}")
    print(f"    Neutral: {dashboard['bias_summary']['neutral']}")
    print(f"  Self-eval Accuracy: {dashboard['accuracy']['accuracy']:.1%}")
    print(f"  Total Runs: {dashboard['accuracy']['total_runs']}")
    print(f"  Recent Events: {len(dashboard['recent_events'])}")
