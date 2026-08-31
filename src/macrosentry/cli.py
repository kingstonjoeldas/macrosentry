"""CLI entry point."""
import argparse
import logging
from .pipeline import MacroSentryPipeline
from .observability import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MacroSentry: Autonomous Fed/market surveillance pipeline"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Run pipeline
    run_parser = subparsers.add_parser("run", help="Run the complete pipeline")
    run_parser.add_argument(
        "--no-store",
        action="store_true",
        help="Run pipeline but don't store results"
    )

    # Dashboard
    dashboard_parser = subparsers.add_parser("dashboard", help="Start dashboard")
    dashboard_parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port for Streamlit app (default: 8501)"
    )

    # Test individual components
    test_parser = subparsers.add_parser("test", help="Test individual components")
    test_parser.add_argument(
        "component",
        choices=["ingestion", "rag", "classification", "evaluation", "storage"],
        help="Component to test"
    )

    args = parser.parse_args()

    if args.command == "run":
        run_pipeline(args.no_store)
    elif args.command == "dashboard":
        run_dashboard(args.port)
    elif args.command == "test":
        test_component(args.component)
    else:
        parser.print_help()


def run_pipeline(no_store: bool = False):
    """Run the complete pipeline."""
    logger.info("Starting MacroSentry pipeline")

    pipeline = MacroSentryPipeline()
    result = pipeline.run()

    # Print results
    print(f"\n{'='*70}")
    print(f"MacroSentry Pipeline Result")
    print(f"{'='*70}")
    print(f"Run ID: {result['run_id']}")
    print(f"Events Processed: {result['events_processed']}")
    print(f"Accuracy: {result['accuracy']:.1%}")
    print(f"Errors: {len(result['errors'])}")

    if result["errors"]:
        print("\nErrors encountered:")
        for error in result["errors"][:5]:
            print(f"  - {error}")

    dashboard = result["dashboard_data"]
    print(f"\nDashboard Summary:")
    print(f"  Overall Bias: {dashboard['bias_summary']['bias'].upper()}")
    print(f"    Hawkish: {dashboard['bias_summary']['hawkish']}")
    print(f"    Dovish: {dashboard['bias_summary']['dovish']}")
    print(f"    Neutral: {dashboard['bias_summary']['neutral']}")
    print(f"  Self-eval Accuracy: {dashboard['accuracy']['accuracy']:.1%}")
    print(f"  Total Runs: {dashboard['accuracy']['total_runs']}")
    print(f"  Recent Events: {len(dashboard['recent_events'])}")
    print(f"{'='*70}")


def run_dashboard(port: int = 8501):
    """Run the Streamlit dashboard."""
    import subprocess
    import sys

    dashboard_path = "dashboard/app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", dashboard_path, "--server.port", str(port)]

    logger.info(f"Starting dashboard on port {port}")
    subprocess.run(cmd)


def test_component(component: str):
    """Test individual components."""
    if component == "ingestion":
        from .ingestion import Ingester
        logger.info("Testing ingestion...")
        ingester = Ingester()
        events = ingester.ingest_all()
        print(f"✓ Ingested {len(events)} events")
        for event in events[:3]:
            print(f"  - {event.headline[:60]}")

    elif component == "rag":
        from .rag import RAGPipeline
        logger.info("Testing RAG...")
        rag = RAGPipeline()
        results = rag.retrieve_context("Fed raises interest rates")
        print(f"✓ Retrieved {len(results)} documents")
        for result in results:
            print(f"  - {result[:80]}")

    elif component == "classification":
        from .classification import Classifier
        from .ingestion import Ingester
        logger.info("Testing classification...")
        ingester = Ingester()
        classifier = Classifier()
        events = ingester.ingest_all()[:2]
        classified = classifier.classify_batch(events)
        print(f"✓ Classified {len(classified)} events")
        for ce in classified:
            print(f"  - {ce.event.headline[:50]}: {ce.bias} ({ce.impact} impact)")

    elif component == "evaluation":
        from .evaluation import Evaluator
        from .classification import Classifier
        from .ingestion import Ingester
        logger.info("Testing evaluation...")
        ingester = Ingester()
        classifier = Classifier()
        evaluator = Evaluator()
        events = ingester.ingest_all()[:2]
        classified = classifier.classify_batch(events)
        evaluated = evaluator.evaluate_batch(classified)
        accuracy = evaluator.compute_accuracy(evaluated)
        print(f"✓ Evaluated {len(evaluated)} events")
        print(f"  Accuracy: {accuracy:.1%}")

    elif component == "storage":
        from .storage import StorageManager
        logger.info("Testing storage...")
        storage = StorageManager()
        dashboard_data = storage.get_dashboard_data()
        print(f"✓ Storage working")
        print(f"  Accuracy: {dashboard_data['accuracy']['accuracy']:.1%}")
        print(f"  Events: {len(dashboard_data['recent_events'])}")


if __name__ == "__main__":
    main()
