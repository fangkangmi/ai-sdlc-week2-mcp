import unittest
from unittest.mock import patch

from claims.api import submit_claim
from tests.helpers import FIXED_NOW

VALID = {
    "policy_number": "HOM1234567",
    "incident_date": "2026-03-08",
    "amount": "450.00",
    "description": "Water leak from the flat upstairs.",
}


@patch("claims.clock.utc_now", return_value=FIXED_NOW)
class SubmitClaimTest(unittest.TestCase):
    def test_valid_claim_is_accepted(self, _now):
        status, _body = submit_claim(dict(VALID))
        self.assertEqual(status, 201)

    def test_invalid_claim_returns_every_error(self, _now):
        status, body = submit_claim({**VALID, "policy_number": "bad", "amount": "0"})
        self.assertEqual(status, 422)
        self.assertEqual(
            {e["code"] for e in body["errors"]},
            {"POLICY_NUMBER_INVALID", "AMOUNT_NOT_POSITIVE"},
        )

    def test_malformed_date_is_a_bad_request(self, _now):
        status, body = submit_claim({**VALID, "incident_date": "08/03/2026"})
        self.assertEqual(status, 400)
        self.assertEqual(body["errors"][0]["code"], "PAYLOAD_INVALID")
