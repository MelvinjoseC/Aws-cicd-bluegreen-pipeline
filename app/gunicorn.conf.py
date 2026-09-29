"""Production Gunicorn configuration for ECS Fargate deployment behind ALB."""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:" + os.environ.get("PORT", "8080")
backlog = 2048

# Worker processes
# For Fargate container with 256/512 CPU, 2-4 workers or 2 workers x 2 threads is optimal
workers = int(os.environ.get("GUNICORN_WORKERS", "2"))
worker_class = "gthread"
threads = int(os.environ.get("GUNICORN_THREADS", "2"))

# Worker lifecycle & memory leak prevention
# Automatically restart workers after processing a batch of requests
max_requests = 1000
max_requests_jitter = 100

# Timeout & Keepalive settings
# ALB idle timeout is 60s. Keepalive must exceed ALB idle timeout to prevent 502 race conditions.
keepalive = 65
timeout = 30
graceful_timeout = 30

# Process naming
proc_name = "cicd-demo-app"

# Logging configuration
accesslog = "-"  # log to stdout
errorlog = "-"   # log to stderr
loglevel = os.environ.get("LOG_LEVEL", "info").lower()
access_log_format = (
    '{"timestamp": "%(t)s", "remote_ip": "%(h)s", "method": "%(m)s", '
    '"path": "%(U)s", "status": %(s)s, "bytes": %(B)s, '
    '"duration_ms": %(D)s, "request_id": "%({X-Request-ID}o)s"}'
)

def on_starting(server):
    """Invoked just before the master process starts."""
    server.log.info("Starting Gunicorn master process with production configuration")

def on_exit(server):
    """Invoked just before exiting Gunicorn."""
    server.log.info("Gunicorn master process shutting down gracefully")
