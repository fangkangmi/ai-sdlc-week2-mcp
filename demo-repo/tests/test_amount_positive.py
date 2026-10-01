import unittest
from decimal import Decimal

from claims.validation import amount_positive
from tests.helpers import make_claim


class AmountPositiveTest(unittest.TestCase):
    def test_positive_amount_passes(self):
        self.assertIsNone(amount_positive.check(make_claim(amount=Decimal("0.01"))))

    def test_zero_fails(self):
        self.assertEqual(amount_positive.check(make_claim(amount=Decimal("0"))).code, "AMOUNT_NOT_POSITIVE")

    def test_negative_fails(self):
        self.assertEqual(amount_positive.check(make_claim(amount=Decimal("-5"))).code, "AMOUNT_NOT_POSITIVE")
