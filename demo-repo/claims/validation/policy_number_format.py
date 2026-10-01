import re

from claims.errors import ValidationError
from claims.models import Claim

POLICY_NUMBER = re.compile(r"[A-Z]{3}\d{7}")


def check(claim: Claim) -> ValidationError | None:
    if not POLICY_NUMBER.fullmatch(claim.policy_number):
        return ValidationError(
            field="policy_number",
            code="POLICY_NUMBER_INVALID",
            message="Policy number must be three letters followed by seven digits.",
        )
    return None
