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

import unittest

import numpy as np
import pandas as pd
import pytz

from qstrader.broker.broker import BrokerException
from qstrader.broker.simulated_broker import SimulatedBroker
from qstrader.broker.zero_broker_commission import ZeroBrokerCommission
from qstrader import settings


class ExchangeMock(object):
    def __init__(self):
        pass

    def get_latest_asset_bid_ask(self, asset):
        return (np.NaN, np.NaN)


class SimulatedBrokerTests(unittest.TestCase):
    """Tests the SimulatedBroker class."""

    def test_initial_settings_for_default_simulated_broker(self):
        """
        Tests that the SimulatedBroker settings are set
        correctly for default settings.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        exchange = ExchangeMock()

        # Test a default SimulatedBroker
        sb1 = SimulatedBroker(start_dt, exchange)
        self.assertEqual(sb1.start_dt, start_dt)
        self.assertEqual(sb1.cur_dt, start_dt)
        self.assertEqual(sb1.exchange, exchange)
        self.assertEqual(sb1.account_id, None)
        self.assertEqual(sb1.base_currency, "USD")
        self.assertEqual(sb1.initial_funds, 0.0)
        self.assertEqual(
            type(sb1.broker_commission),
            ZeroBrokerCommission
        )
        tcb1 = dict(
            zip(
                settings.CURRENCIES,
                [0.0] * len(settings.CURRENCIES)
            )
        )
        self.assertEqual(sb1.cash_balances, tcb1)
        self.assertEqual(sb1.portfolios, {})
        self.assertEqual(sb1.open_orders, {})

        # Test a SimulatedBroker with some parameters set
        sb2 = SimulatedBroker(
            start_dt, exchange, account_id="ACCT1234",
            base_currency="GBP", initial_funds=1e6,
            broker_commission=ZeroBrokerCommission
        )
        self.assertEqual(sb2.start_dt, start_dt)
        self.assertEqual(sb2.cur_dt, start_dt)
        self.assertEqual(sb2.exchange, exchange)
        self.assertEqual(sb2.account_id, "ACCT1234")
        self.assertEqual(sb2.base_currency, "GBP")
        self.assertEqual(sb2.initial_funds, 1e6)
        self.assertEqual(
            type(sb2.broker_commission),
            ZeroBrokerCommission
        )
        tcb2 = dict(
            zip(
                settings.CURRENCIES,
                [0.0] * len(settings.CURRENCIES)
            )
        )
        tcb2["GBP"] = 1e6
        self.assertEqual(sb2.cash_balances, tcb2)
        self.assertEqual(sb2.portfolios, {})
        self.assertEqual(sb2.open_orders, {})

    def test_bad_set_base_currency(self):
        """
        Checks _set_base_currency raises BrokerException
        if a non-supported currency is attempted to be
        set as the base currency.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        exchange = ExchangeMock()
        with self.assertRaises(BrokerException):
            SimulatedBroker(
                start_dt, exchange, base_currency="XYZ"
            )

    def test_good_set_base_currency(self):
        """
        Checks _set_base_currency sets the currency
        correctly if it is supported by QSTrader.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        exchange = ExchangeMock()
        sb = SimulatedBroker(
            start_dt, exchange, base_currency="AUD"
        )
        self.assertEqual(sb.base_currency, "AUD")

    def test_bad_set_initial_funds(self):
        """
        Checks _set_initial_funds raises BrokerException
        if initial funds amount is negative.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        exchange = ExchangeMock()
        with self.assertRaises(BrokerException):
            SimulatedBroker(
                start_dt, exchange, initial_funds=-56.34
            )

    def test_good_set_initial_funds(self):
        """
        Checks _set_initial_funds sets the initial funds
        correctly if it is a positive floating point value.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        exchange = ExchangeMock()
        sb = SimulatedBroker(start_dt, exchange, initial_funds=1e4)
        self.assertEqual(sb._set_initial_funds(1e4), 1e4)

    def test_all_cases_of_set_broker_commission(self):
        """
        Tests that _set_broker_commission correctly sets the
        appropriate broker commission model depending upon
        user choice.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        exchange = ExchangeMock()

        # Broker commission is None
        bc1 = None
        sb1 = SimulatedBroker(start_dt, exchange)
        self.assertEqual(
            type(sb1._set_broker_commission(bc1)),
            ZeroBrokerCommission
        )

        # Broker commission is specified as a subclass
        # of BrokerCommission abstract base class
        bc2 = ZeroBrokerCommission
        sb2 = SimulatedBroker(
            start_dt, exchange, broker_commission=bc2
        )
        self.assertEqual(
            type(sb2._set_broker_commission(bc2)),
            ZeroBrokerCommission
        )

        # Broker commission is mis-specified and thus
        # raises a BrokerException
        with self.assertRaises(BrokerException):
            SimulatedBroker(
                start_dt, exchange, broker_commission="brokercom"
            )

    def test_set_cash_balances(self):
        """
        Checks _set_cash_balances for zero and non-zero
        initial_funds.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        exchange = ExchangeMock()

        # Zero initial funds
        sb1 = SimulatedBroker(
            start_dt, exchange, initial_funds=0.0
        )
        tcb1 = dict(
            zip(
                settings.CURRENCIES,
                [0.0] * len(settings.CURRENCIES)
            )
        )
        self.assertEqual(sb1._set_cash_balances(), tcb1)

        # Non-zero initial funds
        sb2 = SimulatedBroker(
            start_dt, exchange, initial_funds=12345.0
        )
        tcb2 = dict(
            zip(
                settings.CURRENCIES,
                [0.0] * len(settings.CURRENCIES)
            )
        )
        tcb2["USD"] = 12345.0
        self.assertEqual(sb2._set_cash_balances(), tcb2)

    def test_set_initial_portfolios(self):
        """
        Check _set_initial_portfolios method for return
        of an empty dictionary.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        exchange = ExchangeMock()
        sb = SimulatedBroker(start_dt, exchange)
        self.assertEqual(sb._set_initial_portfolios(), {})

    def test_set_initial_open_orders(self):
        """
        Check _set_initial_open_orders method for return
        of an empty dictionary.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        exchange = ExchangeMock()
        sb = SimulatedBroker(start_dt, exchange)
        self.assertEqual(sb._set_initial_open_orders(), {})


if __name__ == "__main__":
    unittest.main()
