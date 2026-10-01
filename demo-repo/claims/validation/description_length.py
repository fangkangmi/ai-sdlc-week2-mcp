from claims.errors import ValidationError
from claims.models import Claim

MAX_LENGTH = 2000


def check(claim: Claim) -> ValidationError | None:
    if not claim.description.strip():
        return ValidationError(
            field="description",
            code="DESCRIPTION_EMPTY",
            message="Description is required.",
        )
    if len(claim.description) > MAX_LENGTH:
        return ValidationError(
            field="description",
            code="DESCRIPTION_TOO_LONG",
            message=f"Description must be at most {MAX_LENGTH} characters.",
        )
    return None
