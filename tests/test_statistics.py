import unittest
from decimal import Decimal
from qstrader.portfolio.portfolio import Portfolio
from test_portfolio import PriceHandlerMock
from qstrader.statistics.statistics import SimpleStatistics


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

    def test_calculating_statistics(self):
        """
        Purchase/sell multiple lots of AMZN, GOOG
        at various prices/commissions to ensure
        the arithmetic in calculating equity, drawdowns
        and sharpe ratio is correct.
        """
        # Create Statistics object
        price_handler = PriceHandlerMock()
        self.portfolio = Portfolio(price_handler, Decimal("500000.00"))

        portfolio_handler = PortfolioHandlerMock(self.portfolio)
        statistics = SimpleStatistics(portfolio_handler)

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "BOT", "AMZN", 100,
            Decimal("566.56"), Decimal("1.00")
        )
        t = "2000-01-01 00:00:00"
        statistics.update(t)
        self.assertEqual(statistics.equity[t], Decimal("499807.00"))
        self.assertEqual(statistics.drawdowns[t], Decimal("193.00"))
        self.assertEqual(statistics.equity_returns[t], Decimal("-0.0386"))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "BOT", "AMZN", 200,
            Decimal
            ("566.395"), Decimal("1.00")
        )
        t = "2000-01-02 00:00:00"
        statistics.update(t)
        self.assertEqual(statistics.equity[t], Decimal("499455.00"))
        self.assertEqual(statistics.drawdowns[t], Decimal("545.00"))
        self.assertEqual(statistics.equity_returns[t], Decimal("-0.0705"))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "BOT", "GOOG", 200,
            Decimal("707.50"), Decimal("1.00")
        )
        t = "2000-01-03 00:00:00"
        statistics.update(t)
        self.assertEqual(statistics.equity[t], Decimal("499046.00"))
        self.assertEqual(statistics.drawdowns[t], Decimal("954.00"))
        self.assertEqual(statistics.equity_returns[t], Decimal("-0.0820"))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "SLD", "AMZN", 100,
            Decimal("565.83"), Decimal("1.00")
        )
        t = "2000-01-04 00:00:00"
        statistics.update(t)
        self.assertEqual(statistics.equity[t], Decimal("499164.00"))
        self.assertEqual(statistics.drawdowns[t], Decimal("836.00"))
        self.assertEqual(statistics.equity_returns[t], Decimal("0.0236"))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "BOT", "GOOG", 200,
            Decimal("705.545"), Decimal("1.00")
        )
        t = "2000-01-05 00:00:00"
        statistics.update(t)
        self.assertEqual(statistics.equity[t], Decimal("499146.00"))
        self.assertEqual(statistics.drawdowns[t], Decimal("854.00"))
        self.assertEqual(statistics.equity_returns[t], Decimal("-0.0036"))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "SLD", "AMZN", 200,
            Decimal("565.59"), Decimal("1.00")
        )
        t = "2000-01-06 00:00:00"
        statistics.update(t)
        self.assertEqual(statistics.equity[t], Decimal("499335.00"))
        self.assertEqual(statistics.drawdowns[t], Decimal("665.00"))
        self.assertEqual(statistics.equity_returns[t], Decimal("0.0379"))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "SLD", "GOOG", 100,
            Decimal("707.92"), Decimal("1.00")
        )
        t = "2000-01-07 00:00:00"
        statistics.update(t)
        self.assertEqual(statistics.equity[t], Decimal("499580.00"))
        self.assertEqual(statistics.drawdowns[t], Decimal("420.00"))
        self.assertEqual(statistics.equity_returns[t], Decimal("0.0490"))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "SLD", "GOOG", 100,
            Decimal("707.90"), Decimal("0.00")
        )
        t = "2000-01-08 00:00:00"
        statistics.update(t)
        self.assertEqual(statistics.equity[t], Decimal("499824.00"))
        self.assertEqual(statistics.drawdowns[t], Decimal("176.00"))
        self.assertEqual(statistics.equity_returns[t], Decimal("0.0488"))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "SLD", "GOOG", 100,
            Decimal("707.92"), Decimal("0.50")
        )
        t = "2000-01-09 00:00:00"
        statistics.update(t)
        self.assertEqual(statistics.equity[t], Decimal("500069.50"))
        self.assertEqual(statistics.drawdowns[t], Decimal("00.00"))
        self.assertEqual(statistics.equity_returns[t], Decimal("0.0491"))

        # Perform transaction and test statistics at this tick
        self.portfolio.transact_position(
            "SLD", "GOOG", 100,
            Decimal("707.78"), Decimal("1.00")
        )
        t = "2000-01-10 00:00:00"
        statistics.update(t)
        self.assertEqual(statistics.equity[t], Decimal("500300.50"))
        self.assertEqual(statistics.drawdowns[t], Decimal("00.00"))
        self.assertEqual(statistics.equity_returns[t], Decimal("0.0462"))

        # Test that results are calculated correctly.
        results = statistics.get_results()
        self.assertEqual(results["max_drawdown"], Decimal("954.00"))
        self.assertEqual(results["max_drawdown_pct"], Decimal("0.1908"))
        self.assertAlmostEqual(float(results["sharpe"]), 1.8353)

if __name__ == "__main__":
    unittest.main()
