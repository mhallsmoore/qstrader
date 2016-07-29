import unittest

from qstrader.portfolio import Portfolio
from qstrader.price_parser import PriceParser
from qstrader.price_handler.base import AbstractTickPriceHandler


class PriceHandlerMock(AbstractTickPriceHandler):
    def get_best_bid_ask(self, ticker):
        prices = {
            "GOOG": (PriceParser.parse(705.46), PriceParser.parse(705.46)),
            "AMZN": (PriceParser.parse(564.14), PriceParser.parse(565.14)),
        }
        return prices[ticker]


class TestAmazonGooglePortfolio(unittest.TestCase):
    """
    Test a portfolio consisting of Amazon and
    Google/Alphabet with various orders to create
    round-trips for both.

    These orders were carried out in the Interactive Brokers
    demo account and checked for cash, equity and PnL
    equality.
    """
    def setUp(self):
        """
        Set up the Portfolio object that will store the
        collection of Position objects, supplying it with
        $500,000.00 USD in initial cash.
        """
        ph = PriceHandlerMock()
        cash = PriceParser.parse(500000.00)
        self.portfolio = Portfolio(ph, cash)

    def test_calculate_round_trip(self):
        """
        Purchase/sell multiple lots of AMZN and GOOG
        at various prices/commissions to check the
        arithmetic and cost handling.
        """
        # Buy 300 of AMZN over two transactions
        self.portfolio.transact_position(
            "BOT", "AMZN", 100,
            PriceParser.parse(566.56), PriceParser.parse(1.00)
        )
        self.portfolio.transact_position(
            "BOT", "AMZN", 200,
            PriceParser.parse(566.395), PriceParser.parse(1.00)
        )
        # Buy 200 GOOG over one transaction
        self.portfolio.transact_position(
            "BOT", "GOOG", 200,
            PriceParser.parse(707.50), PriceParser.parse(1.00)
        )
        # Add to the AMZN position by 100 shares
        self.portfolio.transact_position(
            "SLD", "AMZN", 100,
            PriceParser.parse(565.83), PriceParser.parse(1.00)
        )
        # Add to the GOOG position by 200 shares
        self.portfolio.transact_position(
            "BOT", "GOOG", 200,
            PriceParser.parse(705.545), PriceParser.parse(1.00)
        )
        # Sell 200 of the AMZN shares
        self.portfolio.transact_position(
            "SLD", "AMZN", 200,
            PriceParser.parse(565.59), PriceParser.parse(1.00)
        )
        # Multiple transactions bundled into one (in IB)
        # Sell 300 GOOG from the portfolio
        self.portfolio.transact_position(
            "SLD", "GOOG", 100,
            PriceParser.parse(704.92), PriceParser.parse(1.00)
        )
        self.portfolio.transact_position(
            "SLD", "GOOG", 100,
            PriceParser.parse(704.90), PriceParser.parse(0.00)
        )
        self.portfolio.transact_position(
            "SLD", "GOOG", 100,
            PriceParser.parse(704.92), PriceParser.parse(0.50)
        )
        # Finally, sell the remaining GOOG 100 shares
        self.portfolio.transact_position(
            "SLD", "GOOG", 100,
            PriceParser.parse(704.78), PriceParser.parse(1.00)
        )

        # The figures below are derived from Interactive Brokers
        # demo account using the above trades with prices provided
        # by their demo feed.
        self.assertEqual(len(self.portfolio.positions), 0)
        self.assertEqual(len(self.portfolio.closed_positions), 2)
        self.assertEqual(PriceParser.display(self.portfolio.cur_cash), 499100.50)
        self.assertEqual(PriceParser.display(self.portfolio.equity), 499100.50)
        self.assertEqual(PriceParser.display(self.portfolio.unrealised_pnl), 0.00)
        self.assertEqual(PriceParser.display(self.portfolio.realised_pnl), -899.50)


if __name__ == "__main__":
    unittest.main()
