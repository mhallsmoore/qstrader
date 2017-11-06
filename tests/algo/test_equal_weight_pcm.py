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
from qstrader.broker.td_direct_broker_commission import (
    TDDirectBrokerCommission
)
from qstrader.broker.zero_broker_commission import (
    ZeroBrokerCommission
)
from qstrader.broker.transaction import Transaction
from qstrader.exchange.equity import Equity
from qstrader.algo.forecast import Forecast
from qstrader.algo.order import Order
from qstrader.algo.equal_weight_pcm import EqualWeightPCM
from qstrader.algo.pcm import (
    PortfolioConstructionModel, PortfolioConstructionModelException
)
from .test_portfolio_construction_model import check_equal_order_properties


class ExchangeMock(object):
    def __init__(self, assets, prices):
        self.assets = assets
        self.prices = prices
        self.asset_pvd = {
            asset: (self.prices[i], self.prices[i])
            for i, asset in enumerate(self.assets)
        }

    def _set_hardcoded_asset_price(self, asset, price):
        self.asset_pvd[asset] = (price, price)

    def get_latest_asset_bid_ask(self, asset):
        return self.asset_pvd[asset]


class EqualWeightPCMTests(unittest.TestCase):
    """Tests the EqualWeightPCM derived portfolio construction
    model class.
    """

    def test_no_forecasts_portfolio_remains_in_cash(self):
        """
        Tests that if no forecasts are provided then an empty
        portfolio remains in cash (i.e no orders are generated).
        """
        # Create timestamps
        start_dt = pd.Timestamp('2017-01-01 12:00:00', tz=pytz.UTC)
        cash = 2500000.0

        # Create assets and forecasts
        assets = [
            Equity("%s Inc." % ticker, ticker, "NYSE")
            for ticker in [
                "%s" % (letter*3)
                for letter in string.ascii_uppercase[:9]
            ]
        ]
        forecasts = []

        # Create Exchange and SimulatedBroker
        prices = [
            45.34, 26.58, 62.432, 88.123, 12.876,
            103.56, 229.54, 650.98, 998.123
        ]
        exchange = ExchangeMock(assets, prices)
        zcm = ZeroBrokerCommission()
        broker = SimulatedBroker(
            start_dt, exchange,
            account_id=1234,
            initial_funds=cash,
            broker_commission=zcm
        )
        bpid = "2222"
        broker.create_portfolio(bpid)
        broker.subscribe_funds_to_portfolio(bpid, cash)

        # Create portfolio construction model
        ewpcm = EqualWeightPCM(
            start_dt, broker, bpid,
            transaction_cost_model=zcm
        )

        # Calculate order equivalence
        order_list = ewpcm.generate_orders(forecasts)
        test_order_list = []
        check_equal_order_properties(self, order_list, test_order_list)

    def test_no_forecasts_portfolio_fully_liquidates(self):
        """
        Tests that if no forecasts are provided then a
        portfolio with some assets is fully liquidated
        (and the correct orders are generated).
        """
                # Create timestamps
        start_dt = pd.Timestamp('2017-01-01 12:00:00', tz=pytz.UTC)
        cash = 2500000.0

        # Create assets and forecasts
        assets = [
            Equity("%s Inc." % ticker, ticker, "NYSE")
            for ticker in [
                "%s" % (letter*3)
                for letter in string.ascii_uppercase[:9]
            ]
        ]
        forecasts = []

        # Create Exchange and SimulatedBroker
        prices = [
            45.34, 26.58, 62.432, 88.123, 12.876,
            103.56, 229.54, 650.98, 998.123
        ]
        exchange = ExchangeMock(assets, prices)
        zcm = ZeroBrokerCommission()
        broker = SimulatedBroker(
            start_dt, exchange,
            account_id=1234,
            initial_funds=cash,
            broker_commission=zcm
        )
        bpid = "2222"
        broker.create_portfolio(bpid)
        broker.subscribe_funds_to_portfolio(bpid, cash)

        tn1 = Transaction(
            assets[0], 100, start_dt, price=45.78, 
            order_id=1, commission=0.0
        )
        tn2 = Transaction(
            assets[1], 200, start_dt, price=26.32,
            order_id=2, commission=0.0
        )
        tn3 = Transaction(
            assets[2], -100, start_dt, price=62.432,
            order_id=3, commission=0.0
        )
        broker.portfolios[bpid].transact_asset(tn1)
        broker.portfolios[bpid].transact_asset(tn2)
        broker.portfolios[bpid].transact_asset(tn3)

        # Create portfolio construction model
        ewpcm = EqualWeightPCM(
            start_dt, broker, bpid,
            transaction_cost_model=zcm
        )

        # Calculate order equivalence
        order_list = ewpcm.generate_orders(forecasts)
        test_order_list = [
            Order(start_dt, assets[0], -100),
            Order(start_dt, assets[1], -200),
            Order(start_dt, assets[2], 100),
        ]
        check_equal_order_properties(self, order_list, test_order_list)

    def test_nine_assets_with_zero_commission(self):
        """
        Test creation of correct orders for a nine Equity
        portfolio, with varying positive forecasts and
        varying prices mocked by an ExchangeMock entity.
        This test uses zero commission and zero tax.
        """
        # Create timestamps
        start_dt = pd.Timestamp('2017-01-01 12:00:00', tz=pytz.UTC)
        forecast_dt = pd.Timestamp('2017-01-02 12:00:00', tz=pytz.UTC)
        cash = 500000.0

        # Create assets and forecasts
        assets = [
            Equity("%s Inc." % ticker, ticker, "NYSE")
            for ticker in [
                "%s" % (letter*3)
                for letter in string.ascii_uppercase[:9]
            ]
        ]
        forecasts = [
            Forecast(assets[i], val, start_dt, forecast_dt)
            for i, val in enumerate(
                [
                    0.5, 0.25, 0.3, 0.8, 0.87,
                    0.99, 0.35, 0.28, 0.47
                ]
            )
        ]

        # Create Exchange and SimulatedBroker
        prices = [
            45.34, 26.58, 62.432, 88.123, 12.876,
            103.56, 229.54, 650.98, 998.123
        ]
        exchange = ExchangeMock(assets, prices)
        zcm = ZeroBrokerCommission()
        broker = SimulatedBroker(
            start_dt, exchange,
            account_id=1234,
            initial_funds=cash,
            broker_commission=zcm
        )
        bpid = "2222"
        broker.create_portfolio(bpid)
        broker.subscribe_funds_to_portfolio(bpid, cash)

        # Create portfolio construction model
        ewpcm = EqualWeightPCM(
            start_dt, broker, bpid,
            transaction_cost_model=zcm
        )

        # Calculate order equivalence
        order_list = ewpcm.generate_orders(forecasts)
        test_order_list = [
            Order(start_dt, assets[i], val)
            for i, val in enumerate(
                [
                    1225, 2090, 889, 630, 4314,
                    536, 242, 85, 55
                ]
            )
        ]
        check_equal_order_properties(self, order_list, test_order_list)

    def test_four_assets_with_td_commission(self):
        """
        Test creation of correct orders for a four Equity
        portfolio, with varying positive forecasts and varying
        prices mocked by an ExchangeMock entity. This test uses
        TD Direct commission and tax.
        """
        # Create timestamps
        start_dt = pd.Timestamp('2017-01-01 12:00:00', tz=pytz.UTC)
        forecast_dt = pd.Timestamp('2017-01-02 12:00:00', tz=pytz.UTC)
        cash = 100000.0

        # Create assets and forecasts
        assets = [
            Equity("%s Inc." % ticker, ticker, "NYSE")
            for ticker in ["AAA", "BBB", "CCC", "DDD"]
        ]
        forecasts = [
            Forecast(assets[i], val, start_dt, forecast_dt)
            for i, val in enumerate([1.7, 2.8, 6.32, 36.8])
        ]

        # Create Exchange and SimulatedBroker
        prices = [24.68, 52.55, 63.85, 128.223]
        exchange = ExchangeMock(assets, prices)
        tdcm = TDDirectBrokerCommission()
        broker = SimulatedBroker(
            start_dt, exchange,
            account_id=1234,
            initial_funds=cash,
            broker_commission=tdcm
        )
        bpid = "5678"
        broker.create_portfolio(portfolio_id="5678")
        broker.subscribe_funds_to_portfolio("5678", cash)

        # Create portfolio construction model
        ewpcm = EqualWeightPCM(
            start_dt, broker, bpid,
            transaction_cost_model=tdcm
        )

        # Calculate order equivalence
        order_list = ewpcm.generate_orders(forecasts)
        test_order_list = [
            Order(start_dt, assets[i], val)
            for i, val in enumerate(
                [1007, 473, 389, 193]
            )
        ]
        check_equal_order_properties(self, order_list, test_order_list)

    def test_check_maintenance_of_equal_weights_over_time(self):
        """
        Checks that after an initial portfolio construction that the
        EqualWeightPCM maintains equal proportion upon three additional
        price changes and calls to 'generate_orders(..)'.
        """
        raise NotImplementedError(
            "Should write test_check_maintenance_"
            "of_equal_weights_over_time()"
        )


if __name__ == "__main__":
    unittest.main()
