# ADR-005: AWS Secrets Manager with KMS Customer Managed Keys (CMK)

## Status
Accepted

## Context
Non-sensitive configuration (log levels, feature flags) belongs in SSM Parameter Store, while sensitive credentials (API tokens, database credentials) require automatic rotation and envelope encryption.

## Decision
Adopt a hybrid configuration strategy:
- Non-sensitive parameters: SSM Parameter Store (Standard, String).
- Sensitive secrets: AWS Secrets Manager encrypted with a dedicated Customer Managed Key (CMK) with 365-day rotation.
- Direct injection via ECS task definition `secrets` block to avoid exposing plaintext in container logs or environment variables.

## Consequences
- **Positive**: Strict separation of concerns, automated key rotation, audited access via CloudTrail.
- **Negative**: Requires granular IAM permissions for ECS Task Execution role.
