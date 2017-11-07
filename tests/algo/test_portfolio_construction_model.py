# The MIT License (MIT)
#
# Copyright (c) 2015 QuantStart.com, QuarkGluon Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import string
import unittest

import pandas as pd
import pytz

from qstrader.broker.simulated_broker import SimulatedBroker
from qstrader.exchange.equity import Equity
from qstrader.algo.forecast import Forecast
from qstrader.algo.order import Order
from qstrader.algo.pcm import (
    PortfolioConstructionModel, PortfolioConstructionModelException
)


def check_equal_order_properties(test_class, diff_orders, test_orders):
    """
    Check attributes of the Orders generated between the
    test and diff orders.
    """
    test_class.assertEqual(
        [
            (o.created_dt, o.asset.symbol, o.quantity) 
            for o in diff_orders
        ],
        [
            (o.created_dt, o.asset.symbol, o.quantity) 
            for o in test_orders
        ]
    )


class ExchangeMock(object):
    def __init__(self):
        pass


class RiskModelMock(object):
    def __init__(self):
        pass


class TransactionCostModelMock(object):
    def __init__(self):
        pass


class PortfolioConstructionModelTests(unittest.TestCase):
    """Tests the PortfolioConstructionModel base class.
    """

    def setUp(self):
        """
        Set up a default PortfolioConstructionModel.
        """
        self.start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)

        # Create broker and set up portfolio
        self.exchange = ExchangeMock()
        self.broker = SimulatedBroker(self.start_dt, self.exchange)
        self.broker_portfolio_id = 1234
        self.broker.create_portfolio(portfolio_id=self.broker_portfolio_id)

        # Create risk, TC and portfolio construction models
        self.rmm = RiskModelMock()
        self.tcmm = TransactionCostModelMock()
        self.pcm = PortfolioConstructionModel(
            self.start_dt, self.broker, 
            self.broker_portfolio_id, 
            self.rmm, self.tcmm
        )

        # Generate 20 tickers of the form "AAA", "BBB",
        # ..., "SSS", TTT".
        self.assets = dict( 
            (k,v) for k, v in [
                (letter*3, Equity("%s Inc." % letter*3, letter*3, "NYSE"))
                for letter in string.ascii_uppercase[:20]
            ]
        )

    def test_initial_settings_for_default_model(self):
        """
        Test that the initial settings are as they should be
        for two specified portfolios.
        """
        # Test the default PCM as a sanity check
        self.assertEqual(self.pcm.start_dt, self.start_dt)
        self.assertEqual(self.pcm.broker, self.broker)
        self.assertEqual(
            self.pcm.broker_portfolio_id, 
            self.broker_portfolio_id
        )
        self.assertEqual(self.pcm.risk_model, self.rmm)
        self.assertEqual(self.pcm.transaction_cost_model, self.tcmm)
        self.assertEqual(self.pcm.forecasts, [])
        self.assertEqual(self.pcm.cur_dt, self.start_dt)

    def test_check_sane_forecasts_incorrect(self):
        """
        Test '_check_sane_forecasts' for bad forecasts, including
        dates before current date.
        """
        start_dt = pd.Timestamp("2017-01-05 08:00:00")
        forecast_dt = pd.Timestamp("2017-01-06 08:00:00")
        fc_bad_assets = [
            Forecast(254, -1.0, start_dt, forecast_dt)
            for ticker, asset in self.assets.items()
        ]
        fc_bad_values = [
            Forecast(asset, "UP", start_dt, forecast_dt)
            for ticker, asset in self.assets.items()
        ]
        with self.assertRaises(PortfolioConstructionModelException):
            self.pcm._check_sane_forecasts(fc_bad_assets)
        with self.assertRaises(PortfolioConstructionModelException):
            self.pcm._check_sane_forecasts(fc_bad_values)

    def test_check_set_forecasts_correct(self):
        """
        Test '_check_sane_forecasts' for correct forecasts.
        """
        start_dt = pd.Timestamp("2017-01-05 08:00:00")
        forecast_dt = pd.Timestamp("2017-01-06 08:00:00")
        forecasts = [
            Forecast(asset, -1.0, start_dt, forecast_dt)
            for ticker, asset in self.assets.items()
        ]
        self.assertTrue(self.pcm._check_sane_forecasts(forecasts))

    def test_check_long_only_forecasts_negative(self):
        """
        Test '_check_long_only_forecasts' for negative forecast 
        value.
        """
        start_dt = pd.Timestamp("2017-01-05 08:00:00")
        forecast_dt = pd.Timestamp("2017-01-06 08:00:00")
        forecasts = [
            Forecast(asset, -1.0, start_dt, forecast_dt)
            for ticker, asset in self.assets.items()
        ]
        with self.assertRaises(PortfolioConstructionModelException):
            self.pcm._check_long_only_forecasts(forecasts)

    def test_check_long_only_forecasts_correct(self):
        """
        Test '_check_long_only_forecasts' for correct forecasts.
        """
        start_dt = pd.Timestamp("2017-01-05 08:00:00")
        forecast_dt = pd.Timestamp("2017-01-06 08:00:00")
        forecasts = [
            Forecast(asset, 1.0, start_dt, forecast_dt)
            for ticker, asset in self.assets.items()
        ]
        self.assertTrue(self.pcm._check_long_only_forecasts(forecasts))

    def test_construct_desired_alpha_portfolio(self):
        """
        Test _construct_desired_alpha_portfolio returns {}

        Needed because in this base class (which should not be 
        instantiated directly) there is no portfolio construction
        logic directly.
        """
        self.assertEqual(
            self.pcm._construct_desired_alpha_portfolio(), {}
        )

    def test_construct_desired_risk_portfolio(self):
        """
        Test _construct_desired_risk_portfolio returns {}

        Needed because in this base class (which should not be 
        instantiated directly) there is no portfolio construction
        logic directly.
        """
        self.assertEqual(
            self.pcm._construct_desired_risk_portfolio({}), {}
        )

    def test_construct_desired_trans_cost_portfolio(self):
        """
        Test _construct_desired_trans_cost_portfolio returns {}

        Needed because in this base class (which should not be 
        instantiated directly) there is no portfolio construction
        logic directly.
        """
        self.assertEqual(
            self.pcm._construct_desired_trans_cost_portfolio({}), {}
        )

    def test_diff_desired_broker_portfolios_cash_value_keys(self):
        """
        Test the '_diff_desired_broker_portfolios' method for
        the capability to handle 'total_cash' and 'total_value'
        keys in the Portfolio dictionary, which are not Asset
        instances, but rather strings that have a cash value.
        """
        dp = {
            self.assets["AAA"]: {"quantity": -36},
            self.assets["BBB"]: {"quantity": 4632},
            self.assets["CCC"]: {"quantity": 567},
            self.assets["DDD"]: {"quantity": -123},
        }
        bp = {
            "total_cash": 5000.0,
            "total_value": 10832.0,
            self.assets["AAA"]: {"quantity": -24},
            self.assets["BBB"]: {"quantity": 3726},
        }
        diff_orders = self.pcm._diff_desired_broker_portfolios(dp, bp)
        test_orders = [
            Order(self.start_dt, self.assets["AAA"], -12),
            Order(self.start_dt, self.assets["BBB"], 906),
            Order(self.start_dt, self.assets["CCC"], 567),
            Order(self.start_dt, self.assets["DDD"], -123),
        ]
        check_equal_order_properties(self, diff_orders, test_orders)

    def test_diff_desired_broker_portfolios_long_only(self):
        """
        Test the '_diff_desired_broker_portfolios' method for
        long-only desired portfolios of assets against various
        broker portfolios.

        1) Long only desired, zero portfolio at broker
        2) Long only desired, strict subset at broker
        3) Long only desired, exact portfolio at broker
        4) Long only desired, partial intersection at broker
        5) Long only desired, zero intersection at broker
        6) Long only desired, strict superset at broker
        """
        dp = {
            self.assets["AAA"]: {"quantity": 101},
            self.assets["BBB"]: {"quantity": 50},
            self.assets["CCC"]: {"quantity": 25},
            self.assets["DDD"]: {"quantity": 34},
            self.assets["EEE"]: {"quantity": 47},
            self.assets["FFF"]: {"quantity": 99},
            self.assets["GGG"]: {"quantity": 145},
            self.assets["HHH"]: {"quantity": 55},
        }

        # Test #1 - Long only desired, zero portfolio at broker        
        bp1 = {}
        diff_orders1 = self.pcm._diff_desired_broker_portfolios(dp, bp1)
        test_orders1 = [
            Order(self.start_dt, self.assets["AAA"], 101),
            Order(self.start_dt, self.assets["BBB"], 50),
            Order(self.start_dt, self.assets["CCC"], 25),
            Order(self.start_dt, self.assets["DDD"], 34),
            Order(self.start_dt, self.assets["EEE"], 47),
            Order(self.start_dt, self.assets["FFF"], 99),
            Order(self.start_dt, self.assets["GGG"], 145),
            Order(self.start_dt, self.assets["HHH"], 55)
        ]
        check_equal_order_properties(self, diff_orders1, test_orders1)

        # Test #2 - Long only desired, strict subset at broker
        bp2 = {
            self.assets["BBB"]: {"quantity": 76},
            self.assets["CCC"]: {"quantity": 12},
            self.assets["DDD"]: {"quantity": 34},
            self.assets["EEE"]: {"quantity": 49}
        }
        diff_orders2 = self.pcm._diff_desired_broker_portfolios(dp, bp2)
        test_orders2 = [
            Order(self.start_dt, self.assets["AAA"], 101),
            Order(self.start_dt, self.assets["BBB"], -26),
            Order(self.start_dt, self.assets["CCC"], 13),
            Order(self.start_dt, self.assets["EEE"], -2),
            Order(self.start_dt, self.assets["FFF"], 99),
            Order(self.start_dt, self.assets["GGG"], 145),
            Order(self.start_dt, self.assets["HHH"], 55)
        ]
        check_equal_order_properties(self, diff_orders2, test_orders2)

        # Test #3 - Long only desired, exact portfolio at broker
        bp3 = {
            self.assets["AAA"]: {"quantity": 101},
            self.assets["BBB"]: {"quantity": 50},
            self.assets["CCC"]: {"quantity": 25},
            self.assets["DDD"]: {"quantity": 34},
            self.assets["EEE"]: {"quantity": 47},
            self.assets["FFF"]: {"quantity": 99},
            self.assets["GGG"]: {"quantity": 145},
            self.assets["HHH"]: {"quantity": 55},
        }
        diff_orders3 = self.pcm._diff_desired_broker_portfolios(dp, bp3)
        test_orders3 = []
        check_equal_order_properties(self, diff_orders3, test_orders3)

        # Test #4 - Long only desired, partial intersection at broker
        bp4 = {
            self.assets["EEE"]: {"quantity": 32},
            self.assets["FFF"]: {"quantity": 88},
            self.assets["GGG"]: {"quantity": 109},
            self.assets["HHH"]: {"quantity": 55},
            self.assets["III"]: {"quantity": 234},
            self.assets["JJJ"]: {"quantity": 8},
        }
        diff_orders4 = self.pcm._diff_desired_broker_portfolios(dp, bp4)
        test_orders4 = [
            Order(self.start_dt, self.assets["AAA"], 101),
            Order(self.start_dt, self.assets["BBB"], 50),
            Order(self.start_dt, self.assets["CCC"], 25),
            Order(self.start_dt, self.assets["DDD"], 34),
            Order(self.start_dt, self.assets["EEE"], 15),
            Order(self.start_dt, self.assets["FFF"], 11),
            Order(self.start_dt, self.assets["GGG"], 36),
            Order(self.start_dt, self.assets["III"], -234),
            Order(self.start_dt, self.assets["JJJ"], -8),
        ]
        check_equal_order_properties(self, diff_orders4, test_orders4)

        # Test #5 - Long only desired, zero intersection at broker
        bp5 = {
            self.assets["III"]: {"quantity": 103},
            self.assets["JJJ"]: {"quantity": 38},
            self.assets["KKK"]: {"quantity": 221},
            self.assets["LLL"]: {"quantity": 59},
            self.assets["MMM"]: {"quantity": 76},
        }
        diff_orders5 = self.pcm._diff_desired_broker_portfolios(dp, bp5)
        test_orders5 = [
            Order(self.start_dt, self.assets["AAA"], 101),
            Order(self.start_dt, self.assets["BBB"], 50),
            Order(self.start_dt, self.assets["CCC"], 25),
            Order(self.start_dt, self.assets["DDD"], 34),
            Order(self.start_dt, self.assets["EEE"], 47),
            Order(self.start_dt, self.assets["FFF"], 99),
            Order(self.start_dt, self.assets["GGG"], 145),
            Order(self.start_dt, self.assets["HHH"], 55),
            Order(self.start_dt, self.assets["III"], -103),
            Order(self.start_dt, self.assets["JJJ"], -38),
            Order(self.start_dt, self.assets["KKK"], -221),
            Order(self.start_dt, self.assets["LLL"], -59),
            Order(self.start_dt, self.assets["MMM"], -76),
        ]
        check_equal_order_properties(self, diff_orders5, test_orders5)

        # Test #6 - Long only desired, strict superset at broker
        bp6 = {
            self.assets["AAA"]: {"quantity": 23},
            self.assets["BBB"]: {"quantity": 75},
            self.assets["CCC"]: {"quantity": 34},
            self.assets["DDD"]: {"quantity": 29},
            self.assets["EEE"]: {"quantity": 48},
            self.assets["FFF"]: {"quantity": 104},
            self.assets["GGG"]: {"quantity": 135},
            self.assets["HHH"]: {"quantity": 65},
            self.assets["III"]: {"quantity": 103},
            self.assets["JJJ"]: {"quantity": 38},
            self.assets["KKK"]: {"quantity": 221},
            self.assets["LLL"]: {"quantity": 59},
            self.assets["MMM"]: {"quantity": 76},
        }
        diff_orders6 = self.pcm._diff_desired_broker_portfolios(dp, bp6)
        test_orders6 = [
            Order(self.start_dt, self.assets["AAA"], 78),
            Order(self.start_dt, self.assets["BBB"], -25),
            Order(self.start_dt, self.assets["CCC"], -9),
            Order(self.start_dt, self.assets["DDD"], 5),
            Order(self.start_dt, self.assets["EEE"], -1),
            Order(self.start_dt, self.assets["FFF"], -5),
            Order(self.start_dt, self.assets["GGG"], 10),
            Order(self.start_dt, self.assets["HHH"], -10),
            Order(self.start_dt, self.assets["III"], -103),
            Order(self.start_dt, self.assets["JJJ"], -38),
            Order(self.start_dt, self.assets["KKK"], -221),
            Order(self.start_dt, self.assets["LLL"], -59),
            Order(self.start_dt, self.assets["MMM"], -76),
        ]
        check_equal_order_properties(self, diff_orders6, test_orders6)

    #def test_diff_desired_broker_portfolios_short_only(self):
        """
        Test the '_diff_desired_broker_portfolios' method for
        short-only desired portfolios of assets against various
        broker portfolios.

        1) Short only desired, zero portfolio at broker
        2) Short only desired, strict subset at broker
        3) Short only desired, exact portfolio at broker
        4) Short only desired, partial intersection at broker
        5) Short only desired, zero intersection at broker
        6) Short only desired, strict superset at broker
        """
    #    raise NotImplementedError(
    #        "Should write test_diff_desired_broker_portfolios_short_only()"
    #    )

    #def test_diff_desired_broker_portfolios_mixed(self):
        """
        Test the '_diff_desired_broker_portfolios' method for
        mixed long/shrot desired portfolios of assets against
        various broker portfolios.

        1) Mixed long/short desired, zero portfolio at broker
        2) Mixed long/short desired, strict subset at broker
        3) Mixed long/short desired, exact portfolio at broker
        4) Mixed long/short desired, partial intersection at broker
        5) Mixed long/short desired, zero intersection at broker
        6) Mixed long/short desired, strict superset at broker
        """
    #    raise NotImplementedError(
    #        "Should write test_diff_desired_broker_portfolios_mixed()"
    #    )

    def test_update_raises_for_incorrect_times(self):
        """
        Test that the 'update' method raises the correct
        exception if an incorrect past time is used as
        an argument.
        """
        # bad_dt is before self.start_dt
        bad_dt = pd.Timestamp('2017-09-05 08:00:00', tz=pytz.UTC)
        with self.assertRaises(PortfolioConstructionModelException):
            self.pcm.update(bad_dt)

    def test_update_correctly_sets(self):
        """
        Test that the 'update' method correctly sets the
        current time if a forward date time is used.
        """
        # good_dt is after self.start_dt
        good_dt = pd.Timestamp('2017-11-06 08:00:00', tz=pytz.UTC)
        self.pcm.update(good_dt)
        self.assertEqual(self.pcm.cur_dt, good_dt)


if __name__ == "__main__":
    unittest.main()
