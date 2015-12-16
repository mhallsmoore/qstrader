from decimal import Decimal
import unittest

from position import Position


class FillEventMock(object):
    """
    A mock object that allows a representation
    of a FillEvent object
    """
    def __init__(
        self, ticker, side, 
        quantity, price, commission
    ):
        self.ticker = ticker
        self.side = side
        self.quantity = quantity
        self.price = price
        self.commission = commission


class TestLongAAPLPosition(unittest.TestCase):
    """
    AAPL longed at 100 shares at ask of $118.12
    with brokerage commission at $1.00 
    """
    def setUp(self):
        """
        Set up the FillEvent and Position object
        to reflect a LONG AAPL open position
        """
        bid = Decimal("118.11")
        ask = Decimal("118.12")
        fill = FillEventMock(
            "AAPL", "LONG", 100, 
            ask, Decimal("1.00")
        )
        self.position = Position(fill, bid, ask)

    def test_calculate_initial_values(self):
        """
        Test the calculation of the initial values
        of the Position object
        """
        self.assertEqual(self.position.ticker, "AAPL")
        self.assertEqual(self.position.side, "LONG")
        self.assertEqual(self.position.quantity, 100)
        self.assertEqual(self.position.avg_price, Decimal("118.13000"))
        self.assertEqual(self.position.cost_basis, Decimal("11813.00"))
        self.assertEqual(self.position.bid, Decimal("118.11"))
        self.assertEqual(self.position.ask, Decimal("118.12"))
        self.assertEqual(self.position.market_price, Decimal("118.11"))
        self.assertEqual(self.position.market_value, Decimal("11811.00"))
        self.assertEqual(self.position.abs_unrealized_pnl, Decimal("-2.00"))
        self.assertEqual(self.position.per_unrealized_pnl, Decimal("-0.02"))

    def test_update_position_prices(self):
        """
        Update AAPL's bid and ask prices, then check that
        the Position correctly updates it prices
        """
        bid = Decimal("117.43")
        ask = Decimal("117.44")
        self.position.update_position_prices(bid, ask)
        self.assertEqual(self.position.bid, Decimal("117.43"))
        self.assertEqual(self.position.ask, Decimal("117.44"))
        self.assertEqual(self.position.market_price, Decimal("117.43"))
        self.assertEqual(self.position.market_value, Decimal('11743.00'))
        self.assertEqual(self.position.abs_unrealized_pnl, Decimal("-70.00"))
        self.assertEqual(self.position.per_unrealized_pnl, Decimal("-0.59"))


class TestLongDGEPosition(unittest.TestCase):
    """
    DGE longed at 52 shares at ask of £18.87
    with brokerage commission at £8.86 
    """
    def setUp(self):
        """
        Set up the FillEvent and Position object
        to reflect a LONG DGE open position
        """
        bid = Decimal("18.85315")
        ask = Decimal("18.87315")
        fill = FillEventMock(
            "DGE", "LONG", 52, 
            ask, Decimal("8.86")
        )
        self.position = Position(fill, bid, ask)

    def test_calculate_initial_values(self):
        """
        Test the calculation of the initial values
        of the Position object
        """
        self.assertEqual(self.position.ticker, "DGE")
        self.assertEqual(self.position.side, "LONG")
        self.assertEqual(self.position.quantity, 52)
        self.assertEqual(self.position.avg_price, Decimal("19.04353"))
        self.assertEqual(self.position.cost_basis, Decimal("990.26"))
        self.assertEqual(self.position.bid, Decimal("18.85315"))
        self.assertEqual(self.position.ask, Decimal("18.87315"))
        self.assertEqual(self.position.market_price, Decimal("18.85315"))
        self.assertEqual(self.position.market_value, Decimal("980.36"))
        self.assertEqual(self.position.abs_unrealized_pnl, Decimal("-9.90"))
        self.assertEqual(self.position.per_unrealized_pnl, Decimal("-1.00"))

    def test_update_position_prices(self):
        """
        Update DGE's bid and ask prices, then check that
        the Position correctly updates it prices
        """
        bid = Decimal("19.12500")
        ask = Decimal("19.13500")
        self.position.update_position_prices(bid, ask)
        self.assertEqual(self.position.bid, Decimal("19.12500"))
        self.assertEqual(self.position.ask, Decimal("19.13500"))
        self.assertEqual(self.position.market_price, Decimal("19.12500"))
        self.assertEqual(self.position.market_value, Decimal("994.50"))
        self.assertEqual(self.position.abs_unrealized_pnl, Decimal("4.24"))
        self.assertEqual(self.position.per_unrealized_pnl, Decimal("0.43"))


class TestLongRDSBPosition(unittest.TestCase):
    """
    RDSB longed at 53 shares at ask of £18.43
    with brokerage commission at £8.86 
    """
    def setUp(self):
        """
        Set up the FillEvent and Position object
        to reflect a LONG RDSB open position
        """
        bid = Decimal("18.4171")
        ask = Decimal("18.4271")
        fill = FillEventMock(
            "RDSB", "LONG", 53, 
            ask, Decimal("8.83")
        )
        self.position = Position(fill, bid, ask)

    def test_calculate_initial_values(self):
        """
        Test the calculation of the initial values
        of the Position object
        """
        self.assertEqual(self.position.ticker, "RDSB")
        self.assertEqual(self.position.side, "LONG")
        self.assertEqual(self.position.quantity, 53)
        self.assertEqual(self.position.avg_price, Decimal("18.59370"))
        self.assertEqual(self.position.cost_basis, Decimal("985.47"))
        self.assertEqual(self.position.bid, Decimal("18.4171"))
        self.assertEqual(self.position.ask, Decimal("18.4271"))
        self.assertEqual(self.position.market_price, Decimal("18.4171"))
        self.assertEqual(self.position.market_value, Decimal("976.11"))
        self.assertEqual(self.position.abs_unrealized_pnl, Decimal("-9.36"))
        self.assertEqual(self.position.per_unrealized_pnl, Decimal("-0.95"))

    def test_update_position_prices(self):
        """
        Update RDSB's bid and ask prices, then check that
        the Position correctly updates it prices
        """
        bid = Decimal("16.41500")
        ask = Decimal("16.42500")
        self.position.update_position_prices(bid, ask)
        self.assertEqual(self.position.bid, Decimal("16.41500"))
        self.assertEqual(self.position.ask, Decimal("16.42500"))
        self.assertEqual(self.position.market_price, Decimal("16.41500"))
        self.assertEqual(self.position.market_value, Decimal("870.00"))
        self.assertEqual(self.position.abs_unrealized_pnl, Decimal("-115.47"))
        self.assertEqual(self.position.per_unrealized_pnl, Decimal("-11.72"))


class TestLongGOOGPosition(unittest.TestCase):
    """
    GOOG longed at 100 shares at ask of $749.90
    with brokerage commission of $1.00, then a further
    200 shares longed at ask of $749.485, with brokerage
    commission of $1.00
    """
    def setUp(self):
        """
        Set up the FillEvent and Position object
        to reflect a LONG GOOG open position
        """
        init_bid = Decimal("748.57")
        init_ask = Decimal("749.90")
        init_fill = FillEventMock(
            "GOOG", "LONG", 100, 
            init_ask, Decimal("1.00")
        )
        self.position = Position(init_fill, init_bid, init_ask)

    def test_calculate_initial_values(self):
        """
        Test the calculation of the initial values
        of the Position object
        """
        self.assertEqual(self.position.ticker, "GOOG")
        self.assertEqual(self.position.side, "LONG")
        self.assertEqual(self.position.quantity, 100)
        self.assertEqual(self.position.avg_price, Decimal("749.91"))
        self.assertEqual(self.position.cost_basis, Decimal("74991.00"))
        self.assertEqual(self.position.bid, Decimal("748.57"))
        self.assertEqual(self.position.ask, Decimal("749.90"))
        self.assertEqual(self.position.market_price, Decimal("748.57"))
        self.assertEqual(self.position.market_value, Decimal("74857.00"))
        self.assertEqual(self.position.abs_unrealized_pnl, Decimal("-134.00"))
        self.assertEqual(self.position.per_unrealized_pnl, Decimal("-0.18"))

    def test_buy_shares_and_price_updates(self):
        """
        Tests the ability to buy/long new shares for the Position.
        Adds another 200 shares of GOOG to the Position at a new
        market price. Then test for a new bid/ask price and updated
        market value.
        """
        new_bid = Decimal("748.887")
        new_ask = Decimal("749.485")
        new_fill = FillEventMock(
            "GOOG", "LONG", 200,
            new_ask, Decimal("1.00")
        )
        self.position.buy_shares(new_fill, new_bid, new_ask)

        # Test the properties subsequent to the 
        # "buy_shares" method call
        self.assertEqual(self.position.ticker, "GOOG")
        self.assertEqual(self.position.side, "LONG")
        self.assertEqual(self.position.quantity, 300)
        self.assertEqual(self.position.avg_price, Decimal("749.63"))
        self.assertEqual(self.position.cost_basis, Decimal("224889.00"))
        self.assertEqual(self.position.bid, Decimal("748.887"))
        self.assertEqual(self.position.ask, Decimal("749.485"))
        self.assertEqual(self.position.market_price, Decimal("748.887"))
        self.assertEqual(self.position.market_value, Decimal("224666.10"))
        self.assertEqual(self.position.abs_unrealized_pnl, Decimal("-222.90"))
        self.assertEqual(self.position.per_unrealized_pnl, Decimal("-0.10"))

        # Update the bid and ask prices
        bid = Decimal("750.95")
        ask = Decimal("751.57")
        self.position.update_position_prices(bid, ask)
        self.assertEqual(self.position.bid, Decimal("750.95"))
        self.assertEqual(self.position.ask, Decimal("751.57"))
        # Last Price (used by IB to calculate market price)
        bid = Decimal("751.57")
        self.position.update_position_prices(bid, ask)
        self.assertEqual(self.position.market_price, Decimal("751.57"))
        self.assertEqual(self.position.market_value, Decimal("225471.00"))
        self.assertEqual(self.position.abs_unrealized_pnl, Decimal("582.00"))
        self.assertEqual(self.position.per_unrealized_pnl, Decimal("0.26"))


if __name__ == "__main__":
    unittest.main()
