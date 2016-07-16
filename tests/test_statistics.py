import unittest

from test_portfolio import PriceHandlerMock

from qstrader import settings
from qstrader.price_parser import PriceParser
from qstrader.portfolio import Portfolio
from qstrader.statistics.simple import SimpleStatistics


class PortfolioHandlerMock(object):
    def __init__(self, portfolio):
        self.portfolio = portfolio


class TestSimpleStatistics(unittest.TestCase):
    """
    Test the statistics on a portfolio consisting of
    AMZN and GOOG with various orders to create
    round-trips for both.

    We run a simple and short backtest, and check
    arithmetic for equity, return and drawdown
    calculations along the way.
    """
    def setUp(self):
        self.config = settings.TEST

    def test_calculating_statistics(self):
        """
        Purchase/sell multiple lots of AMZN, GOOG
        at various prices/commissions to ensure
        the arithmetic in calculating equity, drawdowns
        and sharpe ratio is correct.
        """
        # Create Statistics object
        price_handler = PriceHandlerMock()
        self.portfolio = Portfolio(price_handler, PriceParser.parse(500000.00))

        portfolio_handler = PortfolioHandlerMock(self.portfolio)
        statistics = SimpleStatistics(self.config, portfolio_handler)

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "BOT", "AMZN", 100,
            PriceParser.parse(566.56), PriceParser.parse(1.00)
        )
        t = "2000-01-01 00:00:00"
        statistics.update(t, portfolio_handler)
        self.assertEqual(statistics.equity[0], PriceParser.parse(499807.00))
        self.assertEqual(statistics.drawdowns[0], PriceParser.parse(193.00))
        self.assertEqual(statistics.equity_returns[0], PriceParser.parse(-0.386))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "BOT", "AMZN", 200,
            PriceParser.parse(566.395), PriceParser.parse(1.00)
        )
        t = "2000-01-02 00:00:00"
        statistics.update(t, portfolio_handler)
        self.assertEqual(statistics.equity[1], PriceParser.parse(499455.00))
        self.assertEqual(statistics.drawdowns[1], PriceParser.parse(545.00))
        self.assertEqual(statistics.equity_returns[1], PriceParser.parse(-0.705))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "BOT", "GOOG", 200,
            PriceParser.parse(707.50), PriceParser.parse(1.00)
        )
        t = "2000-01-03 00:00:00"
        statistics.update(t, portfolio_handler)
        self.assertEqual(statistics.equity[2], PriceParser.parse(499046.00))
        self.assertEqual(statistics.drawdowns[2], PriceParser.parse(954.00))
        self.assertEqual(statistics.equity_returns[2], PriceParser.parse(-0.820))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "SLD", "AMZN", 100,
            PriceParser.parse(565.83), PriceParser.parse(1.00)
        )
        t = "2000-01-04 00:00:00"
        statistics.update(t, portfolio_handler)
        self.assertEqual(statistics.equity[3], PriceParser.parse(499164.00))
        self.assertEqual(statistics.drawdowns[3], PriceParser.parse(836.00))
        self.assertEqual(statistics.equity_returns[3], PriceParser.parse(0.0236))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "BOT", "GOOG", 200,
            PriceParser.parse(705.545), PriceParser.parse(1.00)
        )
        t = "2000-01-05 00:00:00"
        statistics.update(t, portfolio_handler)
        self.assertEqual(statistics.equity[4], PriceParser.parse(499146.00))
        self.assertEqual(statistics.drawdowns[4], PriceParser.parse(854.00))
        self.assertEqual(statistics.equity_returns[4], PriceParser.parse(-0.036))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "SLD", "AMZN", 200,
            PriceParser.parse(565.59), PriceParser.parse(1.00)
        )
        t = "2000-01-06 00:00:00"
        statistics.update(t, portfolio_handler)
        self.assertEqual(statistics.equity[5], PriceParser.parse(499335.00))
        self.assertEqual(statistics.drawdowns[5], PriceParser.parse(665.00))
        self.assertEqual(statistics.equity_returns[5], PriceParser.parse(0.0379))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "SLD", "GOOG", 100,
            PriceParser.parse(707.92), PriceParser.parse(1.00)
        )
        t = "2000-01-07 00:00:00"
        statistics.update(t, portfolio_handler)
        self.assertEqual(statistics.equity[6], PriceParser.parse(499580.00))
        self.assertEqual(statistics.drawdowns[6], PriceParser.parse(420.00))
        self.assertEqual(statistics.equity_returns[6], PriceParser.parse(0.0490))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "SLD", "GOOG", 100,
            PriceParser.parse(707.90), PriceParser.parse(0.00)
        )
        t = "2000-01-08 00:00:00"
        statistics.update(t, portfolio_handler)
        self.assertEqual(statistics.equity[7], PriceParser.parse(499824.00))
        self.assertEqual(statistics.drawdowns[7], PriceParser.parse(176.00))
        self.assertEqual(statistics.equity_returns[7], PriceParser.parse(0.0488))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "SLD", "GOOG", 100,
            PriceParser.parse(707.92), PriceParser.parse(0.50)
        )
        t = "2000-01-09 00:00:00"
        statistics.update(t, portfolio_handler)
        self.assertEqual(statistics.equity[8], PriceParser.parse(500069.50))
        self.assertEqual(statistics.drawdowns[8], PriceParser.parse(00.00))
        self.assertEqual(statistics.equity_returns[8], PriceParser.parse(0.0491))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "SLD", "GOOG", 100,
            PriceParser.parse(707.78), PriceParser.parse(1.00)
        )
        t = "2000-01-10 00:00:00"
        statistics.update(t, portfolio_handler)
        self.assertEqual(statistics.equity[9], PriceParser.parse(500300.50))
        self.assertEqual(statistics.drawdowns[9], PriceParser.parse(00.00))
        self.assertEqual(statistics.equity_returns[9], PriceParser.parse(0.0462))

        # Test that results are calculated correctly.
        results = statistics.get_results()
        self.assertEqual(results["max_drawdown"], 954.00)
        self.assertEqual(results["max_drawdown_pct"], 0.1908)
        self.assertAlmostEqual(float(results["sharpe"]), 1.8353)

if __name__ == "__main__":
    unittest.main()
