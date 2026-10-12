# ADR-004: OpenTelemetry and AWS X-Ray Compatible Distributed Tracing

## Status
Accepted

## Context
Tracing cross-service requests across ALB, ECS microservices, and external backends requires standardized correlation headers to debug latency regressions in canary deployments.

## Decision
Standardize on W3C `traceparent` and AWS X-Ray `X-Amzn-Trace-Id` headers:
- Extract incoming trace headers or generate compliant IDs on edge entry.
- Inject trace ID and span ID into structured JSON logs.
- Propagate headers in downstream HTTP calls and response payloads.

## Consequences
- **Positive**: Unified distributed tracing, instant CloudWatch log searchability via request ID or trace ID.
- **Negative**: Minor CPU overhead for header parsing and ID generation (< 0.5ms).
