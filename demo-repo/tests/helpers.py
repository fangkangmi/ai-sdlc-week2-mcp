from datetime import date, datetime, timezone
from decimal import Decimal

from claims.models import Claim

FIXED_NOW = datetime(2026, 3, 10, 12, 0, tzinfo=timezone.utc)


def make_claim(**overrides) -> Claim:
    fields = dict(
        policy_number="HOM1234567",
        incident_date=date(2026, 3, 8),
        reported_at=FIXED_NOW,
        amount=Decimal("450.00"),
        description="Water leak from the flat upstairs damaged the kitchen ceiling.",
    )
    fields.update(overrides)
    return Claim(**fields)
