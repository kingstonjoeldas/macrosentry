"""Type definitions."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Literal

@dataclass
class RawEvent:
    """Raw fetched event (headline + source)."""
    id: str
    source: Literal["fed_statement", "fed_speech", "econ_calendar", "news"]
    headline: str
    body: str
    published_at: datetime
    url: str
    tickers: list[str] = field(default_factory=list)

@dataclass
class ClassifiedEvent:
    """Event after classification."""
    event: RawEvent
    bias: Literal["hawkish", "dovish", "neutral"]
    impact: Literal["low", "medium", "high"]
    bias_confidence: float
    impact_confidence: float
    summary: str
    entities: dict[str, list[str]]  # NER results

@dataclass
class EvaluatedEvent:
    """Event after price checking (self-eval)."""
    classified: ClassifiedEvent
    price_direction: Literal["up", "down", "flat"] | None
    price_pct_change: float | None
    prediction_correct: bool | None
    evaluated_at: datetime

@dataclass
class PipelineRun:
    """Complete run metadata."""
    run_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    events_processed: int = 0
    errors: list[str] = field(default_factory=list)
    accuracy: Optional[float] = None
