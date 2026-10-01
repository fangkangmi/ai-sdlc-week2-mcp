from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True)
class Claim:
    policy_number: str
    incident_date: date  # date of loss, as entered by the customer
    reported_at: datetime  # UTC timestamp when the claim was submitted
    amount: Decimal  # claimed amount in GBP
    description: str
