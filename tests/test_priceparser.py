import unittest
from qstrader.price_parser import PriceParser

class TestPriceParserOnFloats(unittest.TestCase):
    """
    Test that PriceParser works with floats.
    """
    def setUp(self):
        self.int = 200
        self.float  = 155.5
        self.vol = 30

    def test_price_from_float(self):
        parsed = PriceParser.parse(self.float)
        self.assertEqual(parsed, 155)
        self.assertIsInstance(parsed, float)

    def test_price_from_int(self):
        pass

    def test_vol(self):
        pass
        # parsed = QsNumParser.parse_price(self.vol)
        # self.assertEqual(parsed, 30)
        # self.assertIsInstance(parsed, float)

    def test_display(self):
        pass
        # parsed = QsNumParser.display_price(self.)



class TestQsNumParserOnInts(unittest.TestCase):
    """
    Test that QsNumParser works with ints.
    """
    def test_creation_from_float(self):
        pass

    def test_creation_from_integer(self):
        pass

    def test_display(self):
        pass


if __name__ == "__main__":
    unittest.main()
