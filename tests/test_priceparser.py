import unittest
import numpy as np
from qstrader.price_parser import PriceParser
from qstrader.compat import PY2


class TestPriceParser(unittest.TestCase):
    def setUp(self):
        self.int = 200

        if PY2:
            self.long = long(self.int)  # noqa
        else:
            self.long = self.int

        self.int64 = np.int64(self.int)

        self.float = 10.1234567
        self.rounded_float = 10.0

        self.vol = 30

    def test_price_from_float(self):
        parsed = PriceParser.parse(self.float)
        self.assertEqual(parsed, 101234567)
        self.assertIsInstance(parsed, int)

    def test_price_from_int(self):
        parsed = PriceParser.parse(self.int)
        self.assertEqual(parsed, 200)
        self.assertIsInstance(parsed, int)

    def test_price_from_long(self):
        parsed = PriceParser.parse(self.long)
        self.assertEqual(parsed, 200)
        if PY2:
            self.assertIsInstance(parsed, long)  # noqa
        else:
            self.assertIsInstance(parsed, int)

    def test_price_from_int64(self):
        parsed = PriceParser.parse(self.int64)
        self.assertEqual(parsed, 200)
        self.assertIsInstance(parsed, np.int64)

    def test_rounded_float(self):
        parsed = PriceParser.parse(self.rounded_float)
        # Expect 100,000,000
        self.assertEqual(parsed, 100000000)
        self.assertIsInstance(parsed, int)

    def test_display(self):
        parsed = PriceParser.parse(self.float)
        displayed = PriceParser.display(parsed)
        self.assertEqual(displayed, 10.12)

    def test_unparsed_display(self):
        displayed = PriceParser.display(self.float)
        self.assertEqual(displayed, 10.12)


if __name__ == "__main__":
    unittest.main()
