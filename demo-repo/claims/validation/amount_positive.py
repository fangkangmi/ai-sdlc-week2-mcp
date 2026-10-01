from claims.errors import ValidationError
from claims.models import Claim


def check(claim: Claim) -> ValidationError | None:
    if claim.amount <= 0:
        return ValidationError(
            field="amount",
            code="AMOUNT_NOT_POSITIVE",
            message="Claimed amount must be greater than zero.",
        )
    return None
