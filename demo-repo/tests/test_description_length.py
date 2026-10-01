import unittest

from claims.validation import description_length
from tests.helpers import make_claim


class DescriptionLengthTest(unittest.TestCase):
    def test_normal_description_passes(self):
        self.assertIsNone(description_length.check(make_claim()))

    def test_blank_fails(self):
        self.assertEqual(description_length.check(make_claim(description="   ")).code, "DESCRIPTION_EMPTY")

    def test_at_max_length_passes(self):
        self.assertIsNone(description_length.check(make_claim(description="x" * description_length.MAX_LENGTH)))

    def test_over_max_length_fails(self):
        error = description_length.check(make_claim(description="x" * (description_length.MAX_LENGTH + 1)))
        self.assertEqual(error.code, "DESCRIPTION_TOO_LONG")
