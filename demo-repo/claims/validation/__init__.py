"""Claim validation. Each rule lives in its own module and is registered in RULES."""
from claims.errors import ValidationError
from claims.models import Claim
from claims.validation import amount_positive, description_length, policy_number_format

RULES = [
    policy_number_format.check,
    amount_positive.check,
    description_length.check,
]


def validate(claim: Claim) -> list[ValidationError]:
    errors = []
    for rule in RULES:
        error = rule(claim)
        if error is not None:
            errors.append(error)
    return errors
