# ADR-001: AWS CodeDeploy Blue/Green Traffic Shifting for ECS Fargate

## Status
Accepted

## Context
Deploying stateful or critical customer-facing microservices via rolling updates can introduce transient errors if a faulty revision slips past synthetic unit tests. Rolling deployments also lack deterministic rollback SLAs under degraded conditions.

## Decision
Adopt AWS CodeDeploy ECS Blue/Green deployments utilizing `CodeDeployDefault.ECSCanary10Percent5Minutes`.
- Maintain dual target groups (Blue and Green).
- Route 10% canary traffic to Green for 5 minutes.
- Auto-rollback on CloudWatch Target Group 5XX alarms or P95 latency spikes (>200ms).
- Terminate old Blue tasks after a 5-minute stabilization window.

## Consequences
- **Positive**: Zero-downtime releases, automated rollback without human intervention, minimized blast radius.
- **Negative**: Requires dual target groups, additional deployment time (~10 minutes total).
