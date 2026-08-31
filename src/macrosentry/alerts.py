"""Alert system for high-impact market events."""
import logging
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MarketAlert:
    """Represents a market alert."""

    def __init__(
        self,
        event_id: str,
        headline: str,
        bias: str,
        impact: str,
        confidence: float,
        severity: AlertSeverity,
        timestamp: datetime,
        source: str
    ):
        self.event_id = event_id
        self.headline = headline
        self.bias = bias
        self.impact = impact
        self.confidence = confidence
        self.severity = severity
        self.timestamp = timestamp
        self.source = source
        self.acknowledged = False

    def to_dict(self) -> Dict:
        """Convert alert to dictionary."""
        return {
            "event_id": self.event_id,
            "headline": self.headline,
            "bias": self.bias,
            "impact": self.impact,
            "confidence": self.confidence,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "acknowledged": self.acknowledged
        }


class AlertManager:
    """Manages market alerts and notifications."""

    def __init__(self, email_enabled: bool = False, slack_enabled: bool = False):
        self.alerts: List[MarketAlert] = []
        self.email_enabled = email_enabled
        self.slack_enabled = slack_enabled
        self.alert_history: List[MarketAlert] = []

    def create_alert(
        self,
        event: Dict,
        confidence: float
    ) -> Optional[MarketAlert]:
        """Create an alert from a classified event."""
        # Determine severity based on impact and bias
        impact = event.get("impact", "low").lower()
        bias = event.get("bias", "neutral").lower()
        confidence_score = event.get("bias_confidence", 0.5)

        if impact == "high":
            severity = AlertSeverity.CRITICAL if confidence_score > 0.8 else AlertSeverity.HIGH
        elif impact == "medium":
            severity = AlertSeverity.HIGH if confidence_score > 0.9 else AlertSeverity.MEDIUM
        else:
            severity = AlertSeverity.LOW

        alert = MarketAlert(
            event_id=event.get("id", "unknown"),
            headline=event.get("headline", "")[:200],
            bias=bias,
            impact=impact,
            confidence=confidence_score,
            severity=severity,
            timestamp=datetime.now(),
            source=event.get("source", "unknown")
        )

        self.alerts.append(alert)
        self.alert_history.append(alert)

        logger.info(f"Alert created: {severity.value} - {alert.headline[:80]}")

        # Send notifications if enabled
        if severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            self._send_notifications(alert)

        return alert

    def get_active_alerts(self) -> List[Dict]:
        """Get all active (unacknowledged) alerts."""
        return [a.to_dict() for a in self.alerts if not a.acknowledged]

    def get_critical_alerts(self) -> List[Dict]:
        """Get critical-severity alerts."""
        return [
            a.to_dict() for a in self.alerts
            if a.severity == AlertSeverity.CRITICAL and not a.acknowledged
        ]

    def acknowledge_alert(self, event_id: str) -> bool:
        """Mark an alert as acknowledged."""
        for alert in self.alerts:
            if alert.event_id == event_id:
                alert.acknowledged = True
                logger.info(f"Alert acknowledged: {event_id}")
                return True
        return False

    def get_alert_stats(self) -> Dict:
        """Get alert statistics."""
        active = [a for a in self.alerts if not a.acknowledged]
        critical = [a for a in active if a.severity == AlertSeverity.CRITICAL]
        high = [a for a in active if a.severity == AlertSeverity.HIGH]

        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(active),
            "critical": len(critical),
            "high": len(high),
            "average_confidence": (
                sum(a.confidence for a in self.alerts) / len(self.alerts)
                if self.alerts else 0.0
            )
        }

    def _send_notifications(self, alert: MarketAlert) -> None:
        """Send notifications for high-severity alerts."""
        message = self._format_alert_message(alert)

        if self.email_enabled:
            self._send_email(message, alert)

        if self.slack_enabled:
            self._send_slack(message, alert)

    def _format_alert_message(self, alert: MarketAlert) -> str:
        """Format alert message for notifications."""
        return (
            f"🚨 {alert.severity.value.upper()} ALERT\n"
            f"Event: {alert.headline}\n"
            f"Bias: {alert.bias.upper()}\n"
            f"Impact: {alert.impact.upper()}\n"
            f"Confidence: {alert.confidence:.1%}\n"
            f"Source: {alert.source}\n"
            f"Time: {alert.timestamp.isoformat()}"
        )

    def _send_email(self, message: str, alert: MarketAlert) -> None:
        """Send email notification (placeholder)."""
        # TODO: Implement email sending via SMTP
        logger.info(f"Email notification sent for alert: {alert.event_id}")

    def _send_slack(self, message: str, alert: MarketAlert) -> None:
        """Send Slack notification (placeholder)."""
        # TODO: Implement Slack webhook integration
        logger.info(f"Slack notification sent for alert: {alert.event_id}")


# Global alert manager instance
alert_manager = AlertManager()
