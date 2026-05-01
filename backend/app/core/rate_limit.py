"""Rate limiting configuration using slowapi."""

import os

from slowapi import Limiter
from slowapi.util import get_remote_address


def _get_rate_limit() -> str:
    """Read rate limit from env var, default 100/minute."""
    per_minute = os.getenv("RATE_LIMIT_PER_MINUTE", "100")
    return f"{per_minute}/minute"


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[_get_rate_limit()],
)
