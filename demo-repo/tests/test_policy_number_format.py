import unittest

from claims.validation import policy_number_format
from tests.helpers import make_claim


class PolicyNumberFormatTest(unittest.TestCase):
    def test_valid_policy_number_passes(self):
        self.assertIsNone(policy_number_format.check(make_claim(policy_number="MOT7654321")))

    def test_lowercase_prefix_fails(self):
        error = policy_number_format.check(make_claim(policy_number="hom1234567"))
        self.assertEqual(error.code, "POLICY_NUMBER_INVALID")

    def test_too_few_digits_fails(self):
        error = policy_number_format.check(make_claim(policy_number="HOM123456"))
        self.assertEqual(error.code, "POLICY_NUMBER_INVALID")
