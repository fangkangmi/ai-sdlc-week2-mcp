"""Single source of time for the service. Tests patch utc_now()."""
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
