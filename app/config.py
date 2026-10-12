"""Application configuration schema and environment validation."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    """Immutable application settings validated at process launch."""
    version: str
    port: int
    log_level: str
    rate_limit_enabled: bool
    rate_limit_rps: float
    rate_limit_burst: float
    drain_timeout: int

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load and validate settings from environment variables."""
        port_raw = os.environ.get("PORT", "8080")
        try:
            port = int(port_raw)
            if not (1 <= port <= 65535):
                raise ValueError(f"PORT must be between 1 and 65535, got {port}")
        except ValueError as err:
            raise ValueError(f"Invalid PORT environment variable: {err}")

        log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
        if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            raise ValueError(f"Invalid LOG_LEVEL: {log_level}")

        rate_limit_enabled = os.environ.get("RATE_LIMIT_ENABLED", "true").lower() in ("true", "1", "yes")
        rate_limit_rps = float(os.environ.get("RATE_LIMIT_RPS", "100.0"))
        rate_limit_burst = float(os.environ.get("RATE_LIMIT_BURST", "200.0"))
        drain_timeout = int(os.environ.get("DRAIN_TIMEOUT_SECONDS", "15"))

        return cls(
            version=os.environ.get("APP_VERSION", "1.0.0"),
            port=port,
            log_level=log_level,
            rate_limit_enabled=rate_limit_enabled,
            rate_limit_rps=rate_limit_rps,
            rate_limit_burst=rate_limit_burst,
            drain_timeout=drain_timeout,
        )


CONFIG = AppConfig.from_env()
