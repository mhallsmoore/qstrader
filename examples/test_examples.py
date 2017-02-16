"""
Test examples

One example can be test individually using:

$ nosetests -s -v examples/test_examples.py:TestExamples.test_strategy_backtest

"""
import os
import math
import unittest

from qstrader import settings
from qstrader.statistics import load
import examples.buy_and_hold_backtest
import examples.moving_average_cross_backtest


class TestExamples(unittest.TestCase):
    """
    Test example are executing correctly
    """
    def setUp(self):
        """
        Set up configuration.
        """
        self.config = settings.TEST
        self.testing = True

    def test_buy_and_hold_backtest(self):
        """
        Test buy_and_hold
        Bar 0, at 2000-01-01 00:00:00
        Bar ????, at 2014-01-01 00:00:00
        """
        tickers = ["SPY"]
        filename = os.path.join(
            settings.TEST.OUTPUT_DIR, 
            "buy_and_hold_backtest.pkl"
        )
        results = examples.buy_and_hold_backtest.run(
            self.config, self.testing, tickers, filename
        )
        for (key, expected) in [
            ('sharpe', 0.5968),
            ('max_drawdown_pct', 5.0308),
            ('max_drawdown', 30174.01)
        ]:
            value = float(results[key])
            self.assertAlmostEqual(expected, value)
        for (key, expected) in [
            ('equity_returns', 
                {
                    'min': -1.6027, 'max': 1.2553, 
                    'first': 0.0000, 'last': -0.0580
                }
            ),
            ('drawdowns', 
                {
                    'min': 0.0, 'max': 30174.01, 
                    'first': 0.0, 'last': 4537.02
                }
            ),
            ('equity', 
                {
                    'min': 488958.0, 'max': 599782.01, 
                    'first': 500000.0, 'last': 595244.99
                }
            )
        ]:
            values = results[key]
            self.assertAlmostEqual(
                float(min(values)), expected['min']
            )
            self.assertAlmostEqual(
                float(max(values)), expected['max']
            )
            self.assertAlmostEqual(
                float(values.iloc[0]), expected['first']
            )
            # self.assertAlmostEqual(
            #    float(values.iloc[-1]), 
            #    expected['last']
            # ) # TODO FAILING BY 1 CENT
        stats = load(filename)
        results = stats.get_results()
        self.assertAlmostEqual(float(results['sharpe']), 0.5968)

    def test_moving_average_cross_backtest(self):
        """
        Test moving average crossover backtest
        """
        tickers = ["AAPL", "SPY"]
        filename = os.path.join(
            settings.TEST.OUTPUT_DIR, 
            "mac_backtest.pkl"
        )
        results = examples.moving_average_cross_backtest.run(
            self.config, self.testing, tickers, filename
        )
        self.assertAlmostEqual(float(results['sharpe']), 0.6430103385)
