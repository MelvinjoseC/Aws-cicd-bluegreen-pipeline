# =====================================================================
# Stage 1: Build stage (compile wheels and prepare isolated environment)
# =====================================================================
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# =====================================================================
# Stage 2: Runtime stage (minimal, hardened production container)
# =====================================================================
FROM python:3.12-slim AS runtime

# Set non-interactive and unbuffered python environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/install/bin:${PATH}" \
    PYTHONPATH="/install/lib/python3.12/site-packages:${PYTHONPATH}"

# Create non-privileged system user & group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /sbin/nologin appuser

WORKDIR /app

# Copy installed Python dependencies from builder stage
COPY --from=builder /install /install

# Copy application source and gunicorn config
COPY app.py gunicorn.conf.py ./

# Secure file permissions and switch to non-root user
RUN chown -R appuser:appgroup /app
USER appuser

# Signal ECS Fargate to send SIGTERM on task stop
STOPSIGNAL SIGTERM

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/livez')" || exit 1

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
