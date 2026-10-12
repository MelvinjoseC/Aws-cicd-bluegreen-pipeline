# STRIDE Threat Model & Security Architecture Review

## 1. Executive Summary
This document provides a systematic STRIDE threat assessment of the AWS ECS Fargate Blue/Green CI/CD Pipeline.

## 2. Threat Analysis Matrix

| Threat Category | Potential Attack Vector | Applied Mitigation | Residual Risk |
|---|---|---|---|
| **Spoofing** | Attacker impersonates GitHub Actions CI to push malicious container images to ECR. | AWS OIDC federation with scoped IAM trust policies (`token.actions.githubusercontent.com`). Cosign keyless image signing. | Low |
| **Tampering** | Man-in-the-middle tampering of egress API calls or ingress HTTP requests. | AWS WAFv2 inspecting SQLi/XSS, TLS 1.3 enforced on ALB listeners, AWS PrivateLink VPC endpoints. | Very Low |
| **Repudiation** | Unauthorized infrastructure modifications performed without audit trail. | CloudTrail multi-region audit logs, S3 bucket access logging with KMS encryption, immutable git commit logs. | Low |
| **Information Disclosure** | Leakage of API secrets or database credentials in container environment or logs. | AWS Secrets Manager with KMS CMK, structured JSON logs masking secrets, detect-secrets pre-commit scanning. | Very Low |
| **Denial of Service (DoS)** | Volumetric HTTP flood overwhelming ECS Fargate container instances. | AWS WAF rate-limiting rules (2,000 req/5m), token-bucket application middleware, ECS target-tracking autoscaling. | Low |
| **Elevation of Privilege** | Container escape granting root host access or unauthorized AWS API execution. | Container runs as non-root `appuser` (UID 10001), readonly root filesystem, strict IAM Task Role least privilege. | Negligible |
