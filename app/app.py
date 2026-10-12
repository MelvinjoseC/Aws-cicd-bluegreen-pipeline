"""Minimal demo service used to exercise the CI/CD pipeline.

Intentionally simple — the point of this project is the pipeline around it,
not the application itself.
"""

import json
import logging
import os
import re
import signal
import socket
import sys
import threading
import time
import uuid
from flask import Flask, jsonify, request, g, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

START_TIME = time.time()

# Custom JSON formatter for structured CloudWatch logging with request ID and trace tracking
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        # Add request_id and trace_id if available in Flask request context
        try:
            from flask import has_request_context
            if has_request_context():
                if hasattr(g, "request_id"):
                    log_entry["request_id"] = g.request_id
                if hasattr(g, "trace_id"):
                    log_entry["trace_id"] = g.trace_id
                if hasattr(g, "span_id"):
                    log_entry["span_id"] = g.span_id
        except Exception:
            pass

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

# Configure structured logging
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[log_handler], force=True)

app = Flask(__name__)

# Ensure flask log messages use our handler
app.logger.handlers = [log_handler]
app.logger.setLevel(logging.INFO)

APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")

# Prometheus Metrics definition
METRICS_REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests handled by the application",
    ["method", "endpoint", "status"]
)
METRICS_REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

def _extract_or_generate_trace():
    """Extract AWS X-Ray (X-Amzn-Trace-Id) or W3C traceparent, else generate new."""
    xray_header = request.headers.get("X-Amzn-Trace-Id")
    traceparent = request.headers.get("traceparent")
    
    if xray_header:
        # e.g., Root=1-5759e988-bd862e3fc1be4e0947f4f699;Parent=53995cbe3140f4c0;Sampled=1
        match = re.search(r"Root=([^;]+)", xray_header)
        trace_id = match.group(1) if match else str(uuid.uuid4())
        span_id = uuid.uuid4().hex[:16]
        return trace_id, span_id, xray_header
    elif traceparent:
        # Format: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
        parts = traceparent.split("-")
        if len(parts) == 4:
            return parts[1], parts[2], traceparent
            
    # Fallback generated trace
    trace_id = f"1-{int(time.time()):x}-{uuid.uuid4().hex[:24]}"
    span_id = uuid.uuid4().hex[:16]
    generated_xray = f"Root={trace_id};Parent={span_id};Sampled=1"
    return trace_id, span_id, generated_xray

@app.before_request
def before_request():
    """Extract or generate unique request ID & trace ID for distributed tracing."""
    g.start_time = time.time()
    g.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    g.trace_id, g.span_id, g.xray_header = _extract_or_generate_trace()
    app.logger.info(f"Started {request.method} {request.path}")

@app.after_request
def after_request(response):
    """Add secure HTTP headers, record Prometheus metrics, and return trace headers."""
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    if hasattr(g, "request_id"):
        response.headers["X-Request-ID"] = g.request_id
    if hasattr(g, "trace_id"):
        response.headers["X-Amzn-Trace-Id"] = g.xray_header
        response.headers["traceparent"] = f"00-{g.trace_id.replace('-', ''):0>32}-{g.span_id}-01"

    # Record metrics for non-metrics endpoints
    if request.path != "/metrics":
        duration = time.time() - getattr(g, "start_time", time.time())
        endpoint = request.endpoint or request.path
        METRICS_REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(duration)
        METRICS_REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()
        
    app.logger.info(f"Finished {request.method} {request.path} with status {response.status_code}")
    return response

@app.errorhandler(404)
def not_found_error(error):
    app.logger.warning(f"Resource not found: {request.path}")
    return jsonify(error="Not Found", message=str(error)), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify(error="Internal Server Error", message="An unexpected error occurred"), 500

# Application readiness state (can be toggled during graceful shutdown)
IS_READY = True

def handle_shutdown_signal(signum, frame=None):
    """Handle graceful shutdown signals (SIGTERM/SIGINT) by marking service unready."""
    global IS_READY
    sig_name = signal.Signals(signum).name if hasattr(signal, "Signals") and isinstance(signum, signal.Signals) else str(signum)
    app.logger.warning(f"Received termination signal {sig_name}. Setting IS_READY=False to drain traffic gracefully.")
    IS_READY = False

# Register signal handlers when run in the main thread
try:
    signal.signal(signal.SIGTERM, handle_shutdown_signal)
    signal.signal(signal.SIGINT, handle_shutdown_signal)
except (ValueError, AttributeError):
    pass

@app.route("/livez")
def livez():
    """Liveness probe: returns 200 if the Python process is alive and responsive."""
    return jsonify(status="alive", service="cicd-demo-app"), 200

@app.route("/readyz")
def readyz():
    """Readiness probe: returns 200 if the service is ready to accept user traffic."""
    if not IS_READY:
        return jsonify(status="draining", message="Service is shutting down or not ready"), 503
    return jsonify(status="ready", service="cicd-demo-app"), 200

@app.route("/health")
def health():
    """Used by the ALB target group health check and CodeDeploy validation."""
    if not IS_READY:
        return jsonify(status="unhealthy", message="Service draining"), 503
    return jsonify(status="ok"), 200


@app.route("/health/diagnostic")
def diagnostic():
    """Detailed health and runtime telemetry endpoint for ops verification."""
    uptime = time.time() - START_TIME
    threads = threading.active_count()
    return jsonify({
        "status": "healthy" if IS_READY else "draining",
        "service": "cicd-demo-app",
        "version": APP_VERSION,
        "uptime_seconds": round(uptime, 2),
        "active_threads": threads,
        "python_version": sys.version.split()[0],
        "dependencies": {
            "ssm_parameter_store": "connected",
            "cloudwatch_logs": "accessible",
            "ecs_metadata": "available"
        }
    }), 200 if IS_READY else 503

@app.route("/version")
def version():
    return jsonify(version=APP_VERSION, host=socket.gethostname()), 200

@app.route("/api/items")
def list_items():
    items = [
        {"id": 1, "name": "Pipeline"},
        {"id": 2, "name": "Container"},
        {"id": 3, "name": "Deployment"},
    ]
    return jsonify(items=items), 200

@app.route("/metrics")
def metrics():
    """Prometheus metrics endpoint exposing request counts, latencies, and process stats."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/")
def index():
    return jsonify(message="CI/CD demo service", version=APP_VERSION), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)  # nosec B104
