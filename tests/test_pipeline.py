"""Integration tests for MacroSentry pipeline."""
import pytest
from datetime import datetime
from src.macrosentry.types import RawEvent
from src.macrosentry.ingestion import Ingester
from src.macrosentry.classification import Classifier
from src.macrosentry.evaluation import Evaluator
from src.macrosentry.storage import StorageManager


@pytest.fixture
def test_event():
    """Create a test event."""
    return RawEvent(
        id="test_1",
        source="test",
        headline="Federal Reserve raises interest rates by 50 basis points",
        body="FOMC decision: hawkish on inflation",
        published_at=datetime.now(),
        url="http://example.com",
        tickers=["ES", "ZN"]
    )


def test_ingestion():
    """Test event ingestion."""
    ingester = Ingester()
    events = ingester.ingest_all()

    assert len(events) > 0, "Ingestion should return events"
    assert all(isinstance(e, RawEvent) for e in events)
    assert all(e.headline for e in events)


def test_classification(test_event):
    """Test classification."""
    classifier = Classifier()
    classified = classifier.classify_event(test_event)

    assert classified.bias in ["hawkish", "dovish", "neutral"]
    assert classified.impact in ["low", "medium", "high"]
    assert 0.0 <= classified.bias_confidence <= 1.0
    assert 0.0 <= classified.impact_confidence <= 1.0
    assert classified.summary


def test_evaluation(test_event):
    """Test evaluation."""
    classifier = Classifier()
    evaluator = Evaluator()

    classified = classifier.classify_event(test_event)
    evaluated = evaluator.evaluate_event(classified)

    # Check structure
    assert evaluated.classified == classified
    assert evaluated.evaluated_at


def test_storage():
    """Test storage."""
    storage = StorageManager()
    dashboard_data = storage.get_dashboard_data()

    assert "recent_events" in dashboard_data
    assert "accuracy" in dashboard_data
    assert "bias_summary" in dashboard_data
    assert 0.0 <= dashboard_data["accuracy"]["accuracy"] <= 1.0


def test_rag():
    """Test RAG retrieval."""
    from src.macrosentry.rag import RAGPipeline

    rag = RAGPipeline()
    context = rag.retrieve_context("Fed raises interest rates", top_k=2)

    assert len(context) > 0, "RAG should retrieve context"
    assert all(isinstance(c, str) for c in context)


def test_end_to_end():
    """End-to-end test."""
    ingester = Ingester()
    classifier = Classifier()
    evaluator = Evaluator()

    # Ingest
    events = ingester.ingest_all()[:2]
    assert len(events) > 0

    # Classify
    classified = classifier.classify_batch(events)
    assert len(classified) == len(events)

    # Evaluate
    evaluated = evaluator.evaluate_batch(classified)
    assert len(evaluated) == len(classified)

    # Check accuracy computation
    accuracy = evaluator.compute_accuracy(evaluated)
    assert 0.0 <= accuracy <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
