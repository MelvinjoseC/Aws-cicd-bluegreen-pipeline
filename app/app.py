"""Minimal demo service used to exercise the CI/CD pipeline.

Intentionally simple — the point of this project is the pipeline around it,
not the application itself.
"""

import json
import logging
import os
import socket
import sys
import uuid
from flask import Flask, jsonify, request, g

# Custom JSON formatter for structured CloudWatch logging with request ID tracking
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        # Add request_id if available in Flask request context
        try:
            from flask import has_request_context
            if has_request_context() and hasattr(g, "request_id"):
                log_entry["request_id"] = g.request_id
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

@app.before_request
def before_request():
    """Extract or generate a unique request ID for request tracing."""
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    g.request_id = request_id
    app.logger.info(f"Started {request.method} {request.path}")

@app.after_request
def after_request(response):
    """Add secure HTTP headers and return the request ID to the client."""
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    if hasattr(g, "request_id"):
        response.headers["X-Request-ID"] = g.request_id
        
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

@app.route("/")
def index():
    return jsonify(message="CI/CD demo service", version=APP_VERSION), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
