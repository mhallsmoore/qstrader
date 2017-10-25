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

import collections
import unittest

import numpy as np
import pandas as pd
import pytz

from qstrader.broker.broker import BrokerException
from qstrader.broker.portfolio import Portfolio
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

    def test_subscribe_funds_to_account(self):
        """
        Tests subscribe_funds_to_account method for:
        * Raising BrokerException with negative amount
        * Correctly setting cash_balances for a positive amount
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        exchange = ExchangeMock()
        sb = SimulatedBroker(start_dt, exchange)

        # Raising BrokerException with negative amount
        with self.assertRaises(BrokerException):
            sb.subscribe_funds_to_account(-4306.23)

        # Correctly setting cash_balances for a positive amount
        sb.subscribe_funds_to_account(165303.23)
        self.assertEqual(
            sb.cash_balances[sb.base_currency], 165303.23
        )

    def test_withdraw_funds_from_account(self):
        """
        Tests withdraw_funds_from_account method for:
        * Raising BrokerException with negative amount
        * Raising BrokerException for lack of cash
        * Correctly setting cash_balances for positive amount
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        exchange = ExchangeMock()
        sb = SimulatedBroker(start_dt, exchange, initial_funds=1e6)

        # Raising BrokerException with negative amount
        with self.assertRaises(BrokerException):
            sb.withdraw_funds_from_account(-4306.23)

        # Raising BrokerException for lack of cash
        with self.assertRaises(BrokerException):
            sb.withdraw_funds_from_account(2e6)

        # Correctly setting cash_balances for a positive amount
        sb.withdraw_funds_from_account(3e5)
        self.assertEqual(
            sb.cash_balances[sb.base_currency], 7e5
        )

    def test_get_account_cash_balance(self):
        """
        Tests get_account_cash_balance method for:
        * If currency is None, return the cash_balances
        * If the currency code isn't in the cash_balances
        dictionary, then raise BrokerException
        * Otherwise, return the appropriate cash balance
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        exchange = ExchangeMock()
        sb = SimulatedBroker(
            start_dt, exchange, initial_funds=1000.0
        )

        # If currency is None, return the cash balances
        sbcb1 = sb.get_account_cash_balance()
        tcb1 = dict(
            zip(
                settings.CURRENCIES,
                [0.0] * len(settings.CURRENCIES)
            )
        )
        tcb1["USD"] = 1000.0
        self.assertEqual(
            sbcb1, tcb1
        )

        # If the currency code isn't in the cash_balances
        # dictionary, then raise BrokerException
        with self.assertRaises(BrokerException):
            sb.get_account_cash_balance(currency="XYZ")

        # Otherwise, return appropriate cash balance
        self.assertEqual(
            sb.get_account_cash_balance(currency="USD"), 1000.0
        )
        self.assertEqual(
            sb.get_account_cash_balance(currency="AUD"), 0.0
        )

    def test_create_portfolio(self):
        """
        Tests create_portfolio method for:
        * If portfolio_id already in the dictionary keys,
        raise BrokerException
        * If it isn't, check that they portfolio and open
        orders dictionary was created correctly.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        exchange = ExchangeMock()
        sb = SimulatedBroker(start_dt, exchange)

        # If portfolio_id isn't in the dictionary, then check it
        # was created correctly, along with the orders dictionary
        sb.create_portfolio(portfolio_id=1234, name="My Portfolio")
        self.assertTrue("1234" in sb.portfolios)
        self.assertTrue(isinstance(sb.portfolios["1234"], Portfolio))
        self.assertTrue("1234" in sb.open_orders)
        self.assertTrue(isinstance(sb.open_orders["1234"], collections.deque))

        # If portfolio is already in the dictionary
        # then raise BrokerException
        with self.assertRaises(BrokerException):
            sb.create_portfolio(
                portfolio_id=1234, name="My Portfolio"
            )

    def test_list_all_portfolio(self):
        """
        Tests list_all_portfolios method for:
        * If empty portfolio dictionary, return empty list
        * If non-empty, return sorted list via the portfolio IDs
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        exchange = ExchangeMock()
        sb = SimulatedBroker(start_dt, exchange)

        # If empty portfolio dictionary, return empty list
        self.assertEquals(sb.list_all_portfolios(), [])

        # If non-empty, return sorted list via the portfolio IDs
        sb.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
        sb.create_portfolio(portfolio_id="z154", name="My Portfolio #2")
        sb.create_portfolio(portfolio_id="abcd", name="My Portfolio #3")
        self.assertEqual(
            sorted(
                [
                    p.portfolio_id
                    for p in sb.list_all_portfolios()
                ]
            ),
            ["1234", "abcd", "z154"]
        )

    def test_update_sets_correct_time(self):
        """
        Tests that the update method sets the current
        time correctly.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        new_dt = pd.Timestamp('2017-10-07 08:00:00', tz=pytz.UTC)
        exchange = ExchangeMock()
        sb = SimulatedBroker(start_dt, exchange)
        sb.update(new_dt)
        self.assertEqual(sb.cur_dt, new_dt)


if __name__ == "__main__":
    unittest.main()
