import unittest

from qstrader.price_handler.base import AbstractBarPriceHandler
from qstrader.order.suggested import SuggestedOrder
from qstrader.price_parser import PriceParser
from qstrader.portfolio import Portfolio
from qstrader.position_sizer.rebalance import LiquidateRebalancePositionSizer

class PriceHandlerMock(AbstractBarPriceHandler):
    tickers={
        "AAA":{"adj_close":PriceParser.parse(50.00)},
        "BBB":{"adj_close":PriceParser.parse(100.00)},
    }

class TestLiquidateRebalancePositionSizer(unittest.TestCase):
    def setUp(self):
        price_handler_mock = PriceHandlerMock()
        ticker_weights = {
            "AAA": 0.3,
            "BBB": 0.7
        }
        self.position_sizer = LiquidateRebalancePositionSizer(ticker_weights)
        self.portfolio = Portfolio(price_handler_mock, PriceParser.parse(10000.00))

    def test_will_add_positions(self):
        """
        Tests that the position sizer will open up new positions with
        the correct weights.
        """
        order_a = SuggestedOrder("AAA","BOT",0)
        order_b = SuggestedOrder("BBB","BOT",0)
        self.position_sizer.size_order(self.portfolio, order_a)
        self.position_sizer.size_order(self.portfolio, order_a)
