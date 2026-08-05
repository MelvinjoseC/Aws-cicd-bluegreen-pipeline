"""Minimal demo service used to exercise the CI/CD pipeline.

Intentionally simple — the point of this project is the pipeline around it,
not the application itself.
"""

import json
import logging
import os
import socket
import sys

# Custom JSON formatter for structured CloudWatch logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

# Configure structured logging
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[log_handler], force=True)

from flask import Flask, jsonify

app = Flask(__name__)

# Ensure flask log messages use our handler
app.logger.handlers = [log_handler]
app.logger.setLevel(logging.INFO)

APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")


@app.route("/health")
def health():
    """Used by the ALB target group health check and CodeDeploy validation."""
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
