import unittest
from qstrader.price_parser import PriceParser

class TestPriceParser(unittest.TestCase):
    def setUp(self):
        self.int = 200
        self.float  = 10.1234567
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

    def test_rounded_float(self):
        parsed = PriceParser.parse(self.rounded_float)
        self.assertEqual(parsed, 100000000) #100mn
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
