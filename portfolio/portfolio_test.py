from decimal import Decimal
import unittest

from qstrader.portfolio.portfolio import Portfolio


class PriceHandlerMock(object):
    def __init__(self):
        self.type = "TICK_HANDLER"

    def get_best_bid_ask(self, ticker):
        prices = {
            "GOOG": (Decimal("705.46"), Decimal("705.46")),
            "AMZN": (Decimal("564.14"), Decimal("565.14")),
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
        cash = Decimal("500000.00")
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
            Decimal("566.56"), Decimal("1.00")
        )
        self.portfolio.transact_position(
            "BOT", "AMZN", 200, 
            Decimal("566.395"), Decimal("1.00")
        )
        # Buy 200 GOOG over one transaction
        self.portfolio.transact_position(
            "BOT", "GOOG", 200, 
            Decimal("707.50"), Decimal("1.00")
        )
        # Add to the AMZN position by 100 shares
        self.portfolio.transact_position(
            "SLD", "AMZN", 100, 
            Decimal("565.83"), Decimal("1.00")
        )
        # Add to the GOOG position by 200 shares
        self.portfolio.transact_position(
            "BOT", "GOOG", 200, 
            Decimal("705.545"), Decimal("1.00")
        )
        # Sell 200 of the AMZN shares
        self.portfolio.transact_position(
            "SLD", "AMZN", 200, 
            Decimal("565.59"), Decimal("1.00")
        )
        # Multiple transactions bundled into one (in IB)
        # Sell 300 GOOG from the portfolio
        self.portfolio.transact_position(
            "SLD", "GOOG", 100, 
            Decimal("704.92"), Decimal("1.00")
        )
        self.portfolio.transact_position(
            "SLD", "GOOG", 100, 
            Decimal("704.90"), Decimal("0.00")
        )
        self.portfolio.transact_position(
            "SLD", "GOOG", 100, 
            Decimal("704.92"), Decimal("0.50")
        )
        # Finally, sell the remaining GOOG 100 shares
        self.portfolio.transact_position(
            "SLD", "GOOG", 100, 
            Decimal("704.78"), Decimal("1.00")
        )

        # The figures below are derived from Interactive Brokers
        # demo account using the above trades with prices provided
        # by their demo feed. 
        self.assertEqual(self.portfolio.cur_cash, Decimal("499100.50"))
        self.assertEqual(self.portfolio.equity, Decimal("499100.50"))
        self.assertEqual(self.portfolio.unrealised_pnl, Decimal("0.00"))
        self.assertEqual(self.portfolio.realised_pnl, Decimal("-899.50"))


if __name__ == "__main__":
    unittest.main()
