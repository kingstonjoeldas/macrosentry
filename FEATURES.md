# MacroSentry - Enhanced Features

## 🆕 New Features Added

### 1. **REST API Server** (`src/macrosentry/api.py`)
Full-featured API for programmatic access to MacroSentry data.

**Endpoints:**
- `GET /api/health` - Health check
- `POST /api/run-pipeline` - Trigger pipeline manually
- `GET /api/dashboard` - Get dashboard summary (bias, accuracy, events)
- `GET /api/events?limit=50` - Get recent classified events
- `GET /api/accuracy/history` - Get accuracy trends
- `GET /api/alerts/high-impact` - Get critical alerts
- `GET /api/stats/bias-breakdown` - Bias distribution statistics
- `GET /api/stats/accuracy` - Overall accuracy metrics

**Usage:**
```bash
# Start API server
python -m flask --app src/macrosentry/api run --port 5000

# Trigger pipeline via API
curl -X POST http://localhost:5000/api/run-pipeline

# Get dashboard data
curl http://localhost:5000/api/dashboard

# Filter high-impact alerts
curl http://localhost:5000/api/alerts/high-impact
```

---

### 2. **Advanced Alert System** (`src/macrosentry/alerts.py`)
Real-time alerts for high-impact market events.

**Features:**
- Severity levels: LOW, MEDIUM, HIGH, CRITICAL
- Automatic alert generation based on event impact & confidence
- Alert acknowledgement tracking
- Alert statistics and reporting
- Placeholder for Email/Slack notifications

**Usage:**
```python
from macrosentry.alerts import alert_manager

# Create alert from event
alert = alert_manager.create_alert(event_data, confidence)

# Get active alerts
alerts = alert_manager.get_active_alerts()

# Acknowledge alert
alert_manager.acknowledge_alert(event_id)

# Get alert stats
stats = alert_manager.get_alert_stats()
# Output: {total_alerts, active_alerts, critical, high, avg_confidence}
```

---

### 3. **Ensemble Classification** (`src/macrosentry/ensemble.py`)
Multiple models voting for higher confidence predictions.

**Features:**
- Weighted voting across predictions
- Rules-based impact scoring
- Confidence breakdown per classification
- Keyword-based event impact weighting

**Confidence Levels:**
- High impact events: Fed decisions, policy, economic data
- Medium impact: Earnings, forecasts
- Low impact: Minor announcements

**Usage:**
```python
from macrosentry.ensemble import ensemble_classifier

# Ensemble bias classification
bias, confidence = ensemble_classifier.classify_bias_ensemble(
    text="Fed signals rate cuts ahead",
    model_predictions=[pred1, pred2, pred3]
)
# Output: ("dovish", 0.92)

# Get confidence breakdown
breakdown = ensemble_classifier.get_prediction_confidence_breakdown(event)
```

---

### 4. **Intelligent Caching** (`src/macrosentry/cache.py`)
In-memory cache with TTL for performance optimization.

**Features:**
- Time-to-live (TTL) support
- Automatic eviction when full
- Cache hit/miss statistics
- Pattern-based invalidation

**Usage:**
```python
from macrosentry.cache import event_cache, query_cache

# Store value with 5-min TTL
event_cache.set("key", value, ttl_seconds=300)

# Retrieve value
value = event_cache.get("key")

# Decorator for function caching
@query_cache.cached(ttl_seconds=60)
def get_dashboard_data():
    return expensive_query()

# Get cache statistics
stats = query_cache.get_stats()
# Output: {hits, misses, hit_rate, evictions, size, max_size}
```

**Dashboard Cache:**
```python
from macrosentry.cache import cache_dashboard_data

@cache_dashboard_data(ttl_seconds=30)
def get_dashboard():
    # Cached for 30 seconds
    pass
```

---

### 5. **Input Validation** (`src/macrosentry/validation.py`)
Comprehensive validation for all event types and classifications.

**Validators:**
- Headline validation (length, format)
- Bias classification validation
- Impact level validation
- Confidence score validation (0-1)
- Event source validation
- URL format validation

**Rate Limiter:**
- Prevent API abuse
- Sliding window rate limiting
- Per-endpoint limits

**Safe Utilities:**
- Safe dictionary access
- Safe type conversions
- Text truncation

**Usage:**
```python
from macrosentry.validation import (
    EventValidator, RateLimiter, ErrorRecovery
)

# Validate classified event
is_valid, errors = EventValidator.validate_classified_event(event)
if not is_valid:
    print(f"Validation errors: {errors}")

# Rate limiting
limiter = RateLimiter(max_calls=100, window_seconds=60)
if limiter.is_allowed():
    process_request()

# Safe value access
value = ErrorRecovery.safe_dict_get(
    data, "nested", "key", default=None
)
```

---

## 📊 Architecture Improvements

### Error Handling
- Comprehensive input validation
- Graceful fallbacks for API failures
- Detailed error messages
- Error recovery strategies

### Performance
- Response caching (configurable TTL)
- Database query optimization
- Async-ready structure

### Scalability
- Rate limiting built-in
- Cache eviction policies
- Stateless API design

### Observability
- Cache statistics
- Alert tracking
- Prediction confidence metrics
- Rate limit monitoring

---

## 🚀 Running Enhanced Features

### Start API Server
```bash
python -m flask --app src/macrosentry/api run --port 5000
```

### Start Dashboard with Real-time Updates
```bash
streamlit run dashboard/app.py
```

### Run Full Pipeline with Alerts
```bash
python -c "
from src.macrosentry.pipeline import MacroSentryPipeline
from src.macrosentry.alerts import alert_manager

pipeline = MacroSentryPipeline()
result = pipeline.run()

# Get active alerts
alerts = alert_manager.get_active_alerts()
for alert in alerts:
    print(f'Alert: {alert[\"headline\"]}')
"
```

---

## 📈 Monitoring & Statistics

### Cache Performance
```python
from macrosentry.cache import query_cache

stats = query_cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.1%}")
print(f"Active entries: {stats['size']}/{stats['max_size']}")
```

### Alert Statistics
```python
from macrosentry.alerts import alert_manager

stats = alert_manager.get_alert_stats()
print(f"Critical alerts: {stats['critical']}")
print(f"Average confidence: {stats['average_confidence']:.1%}")
```

### Rate Limit Status
```python
from macrosentry.validation import RateLimiter

limiter = RateLimiter()
stats = limiter.get_stats()
print(f"Remaining calls: {stats['remaining']}/{stats['max_calls']}")
```

---

## 🔐 Security Features

- Input validation on all endpoints
- Rate limiting per IP/endpoint
- Error handling without exposing internals
- Safe type conversions (no crashes on bad input)
- API CORS configuration

---

## 🔜 Future Enhancements

- [ ] Email notifications for alerts
- [ ] Slack webhook integration
- [ ] WebSocket real-time updates
- [ ] PostgreSQL backend (replace in-memory cache)
- [ ] User authentication & API keys
- [ ] Advanced backtesting framework
- [ ] Model A/B testing
- [ ] Confidence calibration

---

## 📝 Code Quality

All new modules include:
- Type hints for all functions
- Comprehensive docstrings
- Error handling
- Logging
- Unit-test ready structure
