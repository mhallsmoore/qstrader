"""
Test examples

One example can be test individually using:

$ nosetests -s -v tests/test_examples.py:TestExamples.test_strategy_backtest

"""
import unittest

from qstrader import settings
import examples.sp500tr_buy_and_hold_backtest
import examples.mac_backtest
import examples.strategy_backtest


class TestExamples(unittest.TestCase):
    """
    Test example are executing correctly
    """
    def setUp(self):
        """
        Set up configuration.
        """
        self.config = settings.TEST

    def test_sp500tr_buy_and_hold(self):
        """
        Test sp500tr_buy_and_hold
        """
        examples.sp500tr_buy_and_hold_backtest.main(self.config, testing=True)

    def test_mac_backtest(self):
        """
        Test mac_backtest
        """
        examples.mac_backtest.main(self.config, testing=True)

    def test_strategy_backtest(self):
        """
        Test strategy_backtest
        """
        examples.strategy_backtest.main(self.config, testing=True)
