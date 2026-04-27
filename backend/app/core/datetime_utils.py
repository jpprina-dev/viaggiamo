"""Datetime helpers.

The DB columns are timezone-aware (``DateTime(timezone=True)``) so any
Python value handed off to the ORM should be timezone-aware too. Using
``datetime.now()`` (naive, local time) silently writes the wrong value.
``utcnow()`` is the project-wide replacement.
"""

from datetime import UTC, datetime


def utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware ``datetime``."""
    return datetime.now(UTC)
