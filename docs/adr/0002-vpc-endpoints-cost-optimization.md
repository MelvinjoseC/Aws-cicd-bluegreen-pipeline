# ADR-002: AWS PrivateLink VPC Endpoints for Cost Optimization and Network Isolation

## Status
Accepted

## Context
Containers running inside private VPC subnets pulled container layers from ECR and sent telemetry to CloudWatch Logs via NAT Gateways. NAT Gateway data processing charges ($0.045/GB) constituted over 60% of network infrastructure spend during heavy deployment cycles.

## Decision
Deploy AWS PrivateLink VPC Endpoints for:
- S3 (Gateway endpoint - zero cost)
- ECR API & DKR (Interface endpoints)
- CloudWatch Logs (Interface endpoint)
- SSM Parameter Store (Interface endpoint)

## Consequences
- **Positive**: All internal AWS API traffic remains within the AWS private backbone, eliminating internet egress and NAT processing fees. Security posture is significantly improved.
- **Negative**: Small hourly cost per Interface VPC endpoint ($0.01/hour), which is heavily offset by NAT Gateway savings.
