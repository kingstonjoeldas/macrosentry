"""Phase 3: Classification - Zero-shot, NER, and summarization via Hugging Face."""
import logging
from typing import Optional
from .schemas import RawEvent, ClassifiedEvent
from .rag import RAGPipeline
from .config import config

logger = logging.getLogger(__name__)

class HFInferenceClient:
    """Mock Hugging Face Inference API client (uses free endpoint pattern)."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or config.HUGGINGFACE_API_KEY
        # Free tier: no auth required for certain models via huggingface.co/api/inference
        self.base_url = "https://huggingface.co/api/inference"

    def zero_shot_classification(self, text: str, labels: list[str]) -> dict:
        """
        Classify text against candidate labels.
        In production: call actual HF Inference API.
        For now: mock implementation that demonstrates the pattern.
        """
        # Mock response (would make actual API call in production)
        import random

        scores = sorted([(l, random.random()) for l in labels], key=lambda x: -x[1])

        return {
            "labels": [s[0] for s in scores],
            "scores": [s[1] for s in scores],
            "top_label": scores[0][0],
            "confidence": scores[0][1]
        }

    def token_classification(self, text: str) -> dict:
        """
        NER: Extract entities (Fed, CPI, gold, etc.).
        Mock implementation.
        """
        entities = []
        keywords = ["Fed", "CPI", "inflation", "gold", "silver", "rate", "Powell", "FOMC"]

        for keyword in keywords:
            if keyword.lower() in text.lower():
                entities.append({
                    "entity": keyword,
                    "score": 0.95,
                    "type": "EVENT_ENTITY"
                })

        return {"entities": entities}

    def summarization(self, text: str, max_length: int = 50) -> dict:
        """
        Summarize text to one sentence.
        Mock implementation.
        """
        # In production: call HF Summarization endpoint
        # For demo: simple heuristic
        sentences = text.split(".")
        summary = sentences[0] if sentences else text[:50]

        return {
            "summary": summary.strip()[:max_length],
            "original_length": len(text),
            "summary_length": len(summary)
        }


class Classifier:
    """Main classification pipeline."""

    def __init__(self):
        self.hf = HFInferenceClient()
        self.rag = RAGPipeline()

    def classify_event(self, event: RawEvent) -> ClassifiedEvent:
        """
        Full classification: bias + impact + entities + summary.
        Uses RAG to ground the classification.
        """
        try:
            # Step 1: Retrieve historical context via RAG
            context = self.rag.format_context_for_classification(event.headline)
            full_text = f"{context}\n\nEvent: {event.headline}"

            # Step 2: Classify sentiment (hawkish/dovish/neutral)
            bias_labels = ["hawkish", "dovish", "neutral"]
            bias_result = self.hf.zero_shot_classification(
                event.headline,
                bias_labels
            )

            # Step 3: Classify impact (low/medium/high)
            impact_labels = ["low impact", "medium impact", "high impact"]
            impact_result = self.hf.zero_shot_classification(
                event.headline,
                impact_labels
            )

            # Step 4: Extract entities
            ner_result = self.hf.token_classification(event.headline)
            entities = {}
            for ent in ner_result["entities"]:
                entity_type = ent.get("type", "unknown")
                if entity_type not in entities:
                    entities[entity_type] = []
                entities[entity_type].append(ent["entity"])

            # Step 5: Summarize
            summary_result = self.hf.summarization(event.headline + " " + event.body)

            # Map impact label to tier
            impact_map = {
                "low impact": "low",
                "medium impact": "medium",
                "high impact": "high"
            }

            classified = ClassifiedEvent(
                event=event,
                bias=bias_result["top_label"],
                bias_confidence=bias_result["confidence"],
                impact=impact_map.get(impact_result["labels"][0], "medium"),
                impact_confidence=impact_result["scores"][0],
                summary=summary_result["summary"],
                entities=entities
            )

            logger.info(
                f"Classified: {event.headline[:50]}... "
                f"({classified.bias}, {classified.impact})"
            )

            return classified

        except Exception as e:
            logger.error(f"Error classifying event: {e}")
            # Return neutral fallback
            return ClassifiedEvent(
                event=event,
                bias="neutral",
                bias_confidence=0.0,
                impact="medium",
                impact_confidence=0.0,
                summary=event.headline,
                entities={}
            )

    def classify_batch(self, events: list[RawEvent]) -> list[ClassifiedEvent]:
        """Classify multiple events."""
        classified = []
        for event in events:
            classified.append(self.classify_event(event))
        logger.info(f"Classified {len(classified)} events")
        return classified


# CLI for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    classifier = Classifier()

    # Test events
    from .ingestion import Ingester
    ingester = Ingester()
    events = ingester.ingest_all()

    classified = classifier.classify_batch(events[:3])

    for ce in classified:
        print(f"\n{ce.event.headline}")
        print(f"  Bias: {ce.bias} ({ce.bias_confidence:.2%})")
        print(f"  Impact: {ce.impact} ({ce.impact_confidence:.2%})")
        print(f"  Summary: {ce.summary}")
        print(f"  Entities: {ce.entities}")
