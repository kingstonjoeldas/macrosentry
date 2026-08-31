"""Input validation and error handling utilities."""
import logging
from typing import Optional, List, Tuple
import re

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error."""
    pass


class EventValidator:
    """Validates raw events and classified events."""

    @staticmethod
    def validate_headline(headline: str, min_length: int = 10, max_length: int = 500) -> Tuple[bool, Optional[str]]:
        """Validate headline text."""
        if not headline or not isinstance(headline, str):
            return False, "Headline must be a non-empty string"

        if len(headline) < min_length:
            return False, f"Headline too short (min {min_length} characters)"

        if len(headline) > max_length:
            return False, f"Headline too long (max {max_length} characters)"

        return True, None

    @staticmethod
    def validate_bias(bias: str) -> Tuple[bool, Optional[str]]:
        """Validate bias classification."""
        valid_biases = ["hawkish", "dovish", "neutral"]
        if bias.lower() not in valid_biases:
            return False, f"Invalid bias. Must be one of: {valid_biases}"
        return True, None

    @staticmethod
    def validate_impact(impact: str) -> Tuple[bool, Optional[str]]:
        """Validate impact classification."""
        valid_impacts = ["low", "medium", "high"]
        if impact.lower() not in valid_impacts:
            return False, f"Invalid impact. Must be one of: {valid_impacts}"
        return True, None

    @staticmethod
    def validate_confidence(confidence: float) -> Tuple[bool, Optional[str]]:
        """Validate confidence score."""
        if not isinstance(confidence, (int, float)):
            return False, "Confidence must be a number"

        if not 0 <= confidence <= 1:
            return False, "Confidence must be between 0 and 1"

        return True, None

    @staticmethod
    def validate_event_source(source: str) -> Tuple[bool, Optional[str]]:
        """Validate event source."""
        valid_sources = [
            "fed_statement", "fed_speech", "econ_calendar", "newsapi",
            "twitter_reuters", "twitter_fed_watchers", "twitter_cmegroup",
            "news_mock"
        ]

        if source not in valid_sources:
            return False, f"Invalid source. Must be one of: {valid_sources}"

        return True, None

    @staticmethod
    def validate_raw_event(event: dict) -> Tuple[bool, List[str]]:
        """Validate a raw event. Returns (is_valid, list of errors)."""
        errors = []

        # Check headline
        valid, error = EventValidator.validate_headline(event.get("headline", ""))
        if not valid:
            errors.append(f"Headline: {error}")

        # Check source
        valid, error = EventValidator.validate_event_source(event.get("source", ""))
        if not valid:
            errors.append(f"Source: {error}")

        # Check URL format
        url = event.get("url", "")
        if url and not EventValidator._is_valid_url(url):
            errors.append("Invalid URL format")

        # Check published_at
        if not event.get("published_at"):
            errors.append("published_at is required")

        return len(errors) == 0, errors

    @staticmethod
    def validate_classified_event(event: dict) -> Tuple[bool, List[str]]:
        """Validate a classified event. Returns (is_valid, list of errors)."""
        errors = []

        # Validate base event
        valid, raw_errors = EventValidator.validate_raw_event(event)
        errors.extend(raw_errors)

        # Validate bias
        valid, error = EventValidator.validate_bias(event.get("bias", ""))
        if not valid:
            errors.append(f"Bias: {error}")

        # Validate impact
        valid, error = EventValidator.validate_impact(event.get("impact", ""))
        if not valid:
            errors.append(f"Impact: {error}")

        # Validate bias confidence
        valid, error = EventValidator.validate_confidence(
            event.get("bias_confidence", 0.5)
        )
        if not valid:
            errors.append(f"Bias confidence: {error}")

        # Validate impact confidence
        valid, error = EventValidator.validate_confidence(
            event.get("impact_confidence", 0.5)
        )
        if not valid:
            errors.append(f"Impact confidence: {error}")

        return len(errors) == 0, errors

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Check if URL has valid format."""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_calls: int = 100, window_seconds: int = 60):
        self.max_calls = max_calls
        self.window = window_seconds
        self.calls = []

    def is_allowed(self) -> bool:
        """Check if call is allowed under rate limit."""
        import time
        now = time.time()

        # Remove old calls outside the window
        self.calls = [c for c in self.calls if now - c < self.window]

        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True

        return False

    def get_stats(self) -> dict:
        """Get rate limit stats."""
        import time
        now = time.time()
        self.calls = [c for c in self.calls if now - c < self.window]

        return {
            "calls_in_window": len(self.calls),
            "max_calls": self.max_calls,
            "window_seconds": self.window,
            "remaining": max(0, self.max_calls - len(self.calls))
        }


class ErrorRecovery:
    """Error recovery strategies."""

    @staticmethod
    def safe_dict_get(d: dict, *keys, default=None):
        """Safely get nested dictionary values."""
        for key in keys:
            if isinstance(d, dict):
                d = d.get(key)
            else:
                return default
        return d if d is not None else default

    @staticmethod
    def safe_float(value, default: float = 0.0) -> float:
        """Safely convert value to float."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_int(value, default: int = 0) -> int:
        """Safely convert value to int."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def truncate_text(text: str, max_length: int = 500) -> str:
        """Safely truncate text."""
        if not text:
            return ""
        return text[:max_length] + ("..." if len(text) > max_length else "")
