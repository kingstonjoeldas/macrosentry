"""REST API Server for MacroSentry - Real-time market event monitoring."""
import logging
from datetime import datetime
from typing import Optional
from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid

from .pipeline import MacroSentryPipeline
from .storage import StorageManager
from .schemas import RawEvent
from .config import config

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize services
pipeline = MacroSentryPipeline()
storage = StorageManager()


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200


@app.route("/api/run-pipeline", methods=["POST"])
def run_pipeline():
    """Manually trigger the pipeline."""
    try:
        logger.info("API: Triggering pipeline")
        result = pipeline.run()

        return jsonify({
            "status": "success",
            "run_id": result["run_id"],
            "events_processed": result["events_processed"],
            "accuracy": round(result["accuracy"], 3),
            "errors": len(result["errors"]),
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"API: Pipeline execution failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    """Get dashboard data (bias, accuracy, recent events)."""
    try:
        data = storage.get_dashboard_data()
        return jsonify({
            "status": "success",
            "bias_summary": data["bias_summary"],
            "accuracy": data["accuracy"],
            "recent_events": data["recent_events"][:20],
            "last_updated": data["last_updated"]
        }), 200
    except Exception as e:
        logger.error(f"API: Dashboard fetch failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/events", methods=["GET"])
def get_events():
    """Get recent classified events."""
    try:
        limit = request.args.get("limit", 50, type=int)
        events = storage.db.get_recent_events(limit=limit)
        return jsonify({
            "status": "success",
            "events": events,
            "count": len(events)
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/accuracy/history", methods=["GET"])
def get_accuracy_history():
    """Get accuracy history over time."""
    try:
        runs = storage.db.runs if hasattr(storage.db, 'runs') else []
        history = [
            {
                "run_id": r["id"],
                "accuracy": r.get("accuracy", 0),
                "events": r.get("events_processed", 0),
                "timestamp": r.get("created_at", "")
            }
            for r in runs[-20:]  # Last 20 runs
        ]
        return jsonify({
            "status": "success",
            "history": history,
            "count": len(history)
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/alerts/high-impact", methods=["GET"])
def get_high_impact_alerts():
    """Get high-impact events that require attention."""
    try:
        events = storage.db.get_recent_events(limit=100)
        high_impact = [
            e for e in events
            if e.get("impact") == "high"
        ]
        return jsonify({
            "status": "success",
            "alerts": high_impact,
            "count": len(high_impact)
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/stats/bias-breakdown", methods=["GET"])
def get_bias_breakdown():
    """Get bias distribution statistics."""
    try:
        bias_stats = storage.db.get_bias_summary()
        return jsonify({
            "status": "success",
            "hawkish": bias_stats["hawkish"],
            "dovish": bias_stats["dovish"],
            "neutral": bias_stats["neutral"],
            "overall_bias": bias_stats["bias"]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/stats/accuracy", methods=["GET"])
def get_accuracy_stats():
    """Get overall accuracy statistics."""
    try:
        stats = storage.db.get_accuracy_stats()
        return jsonify({
            "status": "success",
            "average_accuracy": round(stats["accuracy"], 3),
            "total_runs": stats["total_runs"],
            "events_processed": stats["events_processed"]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"status": "error", "message": "Internal server error"}), 500


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=5000, debug=False)
