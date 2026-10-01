"""Handler for claim submission. HTTP framework wiring lives elsewhere."""
from datetime import date
from decimal import Decimal, InvalidOperation

from claims import clock
from claims.errors import ValidationError
from claims.models import Claim
from claims.validation import validate


def submit_claim(payload: dict) -> tuple[int, dict]:
    try:
        claim = Claim(
            policy_number=payload["policy_number"],
            incident_date=date.fromisoformat(payload["incident_date"]),
            reported_at=clock.utc_now(),
            amount=Decimal(payload["amount"]),
            description=payload.get("description", ""),
        )
    except (KeyError, ValueError, InvalidOperation) as exc:
        error = ValidationError(field="payload", code="PAYLOAD_INVALID", message=str(exc))
        return 400, {"errors": [error.to_dict()]}

    errors = validate(claim)
    if errors:
        return 422, {"errors": [e.to_dict() for e in errors]}
    return 201, {"status": "received", "policy_number": claim.policy_number}
