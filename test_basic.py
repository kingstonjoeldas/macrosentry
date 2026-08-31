#!/usr/bin/env python3
"""Quick test of basic pipeline functionality without heavy dependencies."""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 70)
print("MacroSentry Basic Functionality Test")
print("=" * 70)

# Test 1: Types
print("\n[1/5] Testing type definitions...")
try:
    from macrosentry.types import RawEvent, ClassifiedEvent, EvaluatedEvent, PipelineRun

    event = RawEvent(
        id="test",
        source="test",
        headline="Test headline",
        body="Test body",
        published_at=datetime.now(),
        url="http://example.com"
    )
    print("✓ Type definitions work")
except Exception as e:
    print(f"✗ Type definitions failed: {e}")
    sys.exit(1)

# Test 2: Config
print("\n[2/5] Testing configuration...")
try:
    from macrosentry.config import config
    print(f"✓ Config loaded (tickers: {len(config.TICKERS)})")
except Exception as e:
    print(f"✗ Config failed: {e}")
    sys.exit(1)

# Test 3: Observability
print("\n[3/5] Testing observability...")
try:
    from macrosentry.observability import StructuredLogger, configure_logging
    configure_logging()
    logger = StructuredLogger()
    logger.log_ingestion_start(["test"])
    logs = logger.get_latest_logs(1)
    print(f"✓ Structured logging works ({len(logs)} entries)")
except Exception as e:
    print(f"✗ Observability failed: {e}")
    sys.exit(1)

# Test 4: Storage (mock)
print("\n[4/5] Testing storage...")
try:
    from macrosentry.storage import StorageManager
    storage = StorageManager()
    dashboard = storage.get_dashboard_data()
    print(f"✓ Storage works (accuracy: {dashboard['accuracy']['accuracy']:.1%})")
except Exception as e:
    print(f"✗ Storage failed: {e}")
    sys.exit(1)

# Test 5: Ingestion (mock)
print("\n[5/5] Testing ingestion...")
try:
    from macrosentry.ingestion import Ingester
    ingester = Ingester()
    events = ingester.ingest_all()
    print(f"✓ Ingestion works ({len(events)} events fetched)")
    for i, event in enumerate(events[:3], 1):
        print(f"    {i}. {event.headline[:60]}")
except Exception as e:
    print(f"✗ Ingestion failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ All basic tests passed!")
print("=" * 70)
print("\nNext steps:")
print("1. Install full dependencies:  pip install -r requirements.txt")
print("2. Run full pipeline:          python -m macrosentry run")
print("3. Start dashboard:            python -m macrosentry dashboard")
print("\n")
