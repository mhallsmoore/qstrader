"""
Test examples

One example can be test individually using:

$ nosetests -s -v examples/test_examples.py:TestExamples.test_strategy_backtest

"""
import os
import unittest

from qstrader import settings
import examples.pandas_examples.pandas_bar_display_prices_backtest
import examples.pandas_examples.pandas_tick_strategy_backtest


class TestPandasExamples(unittest.TestCase):
    """
    Test example are executing correctly
    """
    def setUp(self):
        """
        Set up configuration.
        """
        self.config = settings.TEST
        self.testing = True
        self.max_rows = 20
        self.cache_name = ''
        self.cache_backend = 'sqlite'
        self.expire_after = '24:00:00.0'
        self.n = 100
        self.n_window = 5

    def test_pandas_bar_display_prices_backtest(self):
        data_source = 'yahoo'
        start = '2010-01-04'
        end = '2016-06-22'
        tickers = ["^GSPC"]
        filename = os.path.join(settings.TEST.OUTPUT_DIR, "pandas_bar_display_prices_backtest.pkl")
        results = examples.pandas_examples.pandas_bar_display_prices_backtest.run(self.cache_name, self.cache_backend, self.expire_after, data_source, start, end, self.config, self.testing, tickers, filename, self.n, self.n_window)
        self.assertAlmostEqual(float(results['sharpe']), 0.5968)

    def test_pandas_bar_display_prices_backtest_multi(self):
        data_source = 'yahoo'
        start = '2010-01-04'
        end = '2016-06-22'
        tickers = ["MSFT", "GOOG"]
        filename = os.path.join(settings.TEST.OUTPUT_DIR, "pandas_bar_display_prices_backtest_multi.pkl")
        results = examples.pandas_examples.pandas_bar_display_prices_backtest.run(self.cache_name, self.cache_backend, self.expire_after, data_source, start, end, self.config, self.testing, tickers, filename, self.n, self.n_window)
        self.assertAlmostEqual(float(results['sharpe']), 0.3544)

    def test_pandas_tick_strategy_backtest(self):
        tickers = ["GOOG"]
        filename = os.path.join(settings.TEST.OUTPUT_DIR, "pandas_tick_strategy_backtest.pkl")
        results = examples.pandas_examples.pandas_tick_strategy_backtest.run(self.config, self.testing, tickers, filename, self.n, self.n_window)
        self.assertAlmostEqual(float(results['sharpe']), -7.1351)

    def test_pandas_tick_strategy_backtest_multi(self):
        tickers = ["GOOG", "MSFT"]
        filename = os.path.join(settings.TEST.OUTPUT_DIR, "pandas_tick_strategy_backtest_multi.pkl")
        results = examples.pandas_examples.pandas_tick_strategy_backtest.run(self.config, self.testing, tickers, filename, self.n, self.n_window)
        self.assertAlmostEqual(float(results['sharpe']), -5.0262)
