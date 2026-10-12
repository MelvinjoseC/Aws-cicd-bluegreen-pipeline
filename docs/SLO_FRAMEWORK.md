# Enterprise Service Level Objectives (SLO) & Error Budget Policy

## 1. Objective Overview
This document defines the production Service Level Indicators (SLIs), Service Level Objectives (SLOs), and Error Budget policies for the AWS ECS Blue/Green platform.

## 2. Service Level Indicators (SLIs) & Objectives (SLOs)

| Metric | Target | Measurement Window | SLI Definition |
|---|---|---|---|
| **Availability** | **99.95%** | 30-Day Rolling | Ratio of HTTP non-5XX requests to total valid HTTP requests received at ALB |
| **Latency (P95)** | **< 120 ms** | 30-Day Rolling | 95th percentile response latency for successful (`2xx`/`3xx`) requests |
| **Latency (P99)** | **< 350 ms** | 30-Day Rolling | 99th percentile response latency for successful requests |
| **Deployment Success** | **100%** | Per Release | Deployments complete without triggering automatic CodeDeploy rollback |

## 3. Error Budget Consumption & Burn Rate Matrix

| Burn Rate | Budget Consumed | Time to 100% Exhaustion | Action Required |
|---|---|---|---|
| **14.4x** | 2% in 1 hour | 2 days | **P1 Page Alert**: Immediate on-call engagement, pause non-critical deployments. |
| **6.0x** | 5% in 6 hours | 5 days | **P2 High Priority**: Platform team investigation, automated canary throttling. |
| **1.0x** | Steady state | 30 days | Normal operating cadence. |

## 4. Deployment Freeze Policy
When the 30-day error budget drops below **10% remaining**:
1. All feature releases to production are paused.
2. Engineering priority shifts exclusively to reliability, testing, and bug remediation.
3. Deployments resume once the error budget recovers above **25%**.
