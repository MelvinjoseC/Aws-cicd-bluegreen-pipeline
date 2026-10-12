# ADR-003: Keyless Container Signing and Attestation with Sigstore Cosign

## Status
Accepted

## Context
Securing the software supply chain against unauthorized container images or tampering between build and ECS deployment is mandatory for SOC2 and NIST SP 800-218 compliance.

## Decision
Implement Sigstore Cosign in GitHub Actions utilizing OIDC keyless signing:
- Eliminate long-lived cryptographic private keys.
- Sign images in ECR using temporary GitHub Actions OIDC identity tokens.
- Verify container signatures in pipeline pre-deployment gates and attach SLSA provenance attestations.

## Consequences
- **Positive**: Cryptographic provenance verification, zero secret management overhead.
- **Negative**: Adds ~15 seconds to CI pipeline execution.
