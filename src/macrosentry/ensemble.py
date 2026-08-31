"""Ensemble classification - multiple models for high-confidence predictions."""
import logging
from typing import Dict, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


class EnsembleClassifier:
    """Combines multiple classification approaches for ensemble voting."""

    def __init__(self):
        self.models = []
        self.weights = {}

    def classify_bias_ensemble(
        self,
        text: str,
        model_predictions: list
    ) -> Tuple[str, float]:
        """
        Ensemble voting for bias classification.
        Returns (bias_label, confidence_score)
        """
        if not model_predictions:
            return "neutral", 0.5

        # Extract predictions from different sources
        predictions = []
        for pred in model_predictions:
            if isinstance(pred, dict) and "label" in pred:
                predictions.append(pred["label"].lower())

        if not predictions:
            return "neutral", 0.5

        # Weighted voting
        bias_votes = Counter(predictions)
        most_common_bias, vote_count = bias_votes.most_common(1)[0]

        # Calculate confidence based on consensus
        confidence = vote_count / len(predictions)

        logger.info(
            f"Ensemble bias classification: {most_common_bias} "
            f"(confidence: {confidence:.1%}, votes: {vote_count}/{len(predictions)})"
        )

        return most_common_bias, confidence

    def classify_impact_ensemble(
        self,
        text: str,
        event_type: str,
        model_predictions: list
    ) -> Tuple[str, float]:
        """
        Ensemble voting for impact classification.
        Returns (impact_level, confidence_score)
        """
        # Rules-based impact determination
        impact_score = self._calculate_impact_score(text, event_type)

        # Extract model predictions
        predictions = []
        for pred in model_predictions:
            if isinstance(pred, dict) and "label" in pred:
                predictions.append(pred["label"].lower())

        if predictions:
            # Combine rules + ML predictions
            impact_votes = Counter(predictions)
            most_common, vote_count = impact_votes.most_common(1)[0]
            ml_confidence = vote_count / len(predictions)
        else:
            ml_confidence = 0.0
            most_common = self._score_to_impact(impact_score)

        # Blend rules-based and ML confidence
        final_confidence = (impact_score + ml_confidence) / 2
        final_impact = most_common if ml_confidence > 0.6 else self._score_to_impact(impact_score)

        logger.info(
            f"Ensemble impact classification: {final_impact} "
            f"(confidence: {final_confidence:.1%}, rules-score: {impact_score:.2f})"
        )

        return final_impact, final_confidence

    def _calculate_impact_score(self, text: str, event_type: str) -> float:
        """Calculate impact score based on keywords and event type."""
        score = 0.5  # Neutral baseline

        # Event type weighting
        high_impact_events = [
            "fed", "fomc", "rate decision", "policy", "inflation",
            "gdp", "employment", "jobs report", "crisis", "emergency"
        ]
        medium_impact_events = [
            "earnings", "guidance", "forecast", "economic data",
            "treasury", "bond", "yield"
        ]

        text_lower = text.lower()
        event_lower = event_type.lower()

        # Check for high-impact keywords
        if any(keyword in event_lower for keyword in high_impact_events):
            score = 0.8
        elif any(keyword in event_lower for keyword in medium_impact_events):
            score = 0.6

        # Amplify for specific trigger words
        trigger_words = [
            "emergency", "shock", "crisis", "collapse", "surge",
            "unprecedented", "historic", "unexpected", "surprise"
        ]
        if any(word in text_lower for word in trigger_words):
            score = min(1.0, score + 0.2)

        # Reduce if low-impact indicators
        low_impact_words = ["minor", "slight", "marginal", "small"]
        if any(word in text_lower for word in low_impact_words):
            score = max(0.3, score - 0.2)

        return score

    def _score_to_impact(self, score: float) -> str:
        """Convert numeric score to impact label."""
        if score >= 0.7:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"

    def get_prediction_confidence_breakdown(
        self,
        event_data: Dict
    ) -> Dict:
        """Get detailed confidence breakdown for an event."""
        return {
            "event_id": event_data.get("id"),
            "bias": {
                "label": event_data.get("bias"),
                "confidence": event_data.get("bias_confidence", 0),
            },
            "impact": {
                "label": event_data.get("impact"),
                "confidence": event_data.get("impact_confidence", 0),
            },
            "overall_confidence": (
                (event_data.get("bias_confidence", 0) +
                 event_data.get("impact_confidence", 0)) / 2
            ),
            "reliable": event_data.get("bias_confidence", 0) > 0.7
        }


# Global ensemble classifier instance
ensemble_classifier = EnsembleClassifier()
