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

import pandas as pd
import pytz

from qstrader.broker.portfolio import (
    Portfolio, PortfolioException, PortfolioEvent
)
from qstrader.broker.transaction import Transaction
from qstrader.utils.captured_output import captured_output


class EquityMock(object):
    """Mock object for the Asset-derived Equity class."""

    def __init__(
        self, name, symbol,
        exchange, tax_exempt=False
    ):
        self.__name__ = "Equity"
        self.name = name
        self.symbol = symbol
        self.exchange = exchange
        self.tax_exempt = tax_exempt

    def __str__(self):
        return "%s(name='%s', symbol='%s', " \
            "exchange='%s', tax_exempt=%s)" % (
                self.__name__, self.name, self.symbol,
                self.exchange, self.tax_exempt
            )


class PortfolioTests(unittest.TestCase):
    """Tests the Portfolio class.

    Checks for:
    * Initial settings configuration
    * Subscription and withdrawal behaviour
    * Asset transaction behaviour
    * Cash dividend behaviour
    * TODO: Market value of asset behaviour
    * TODO: History dataframe behaviour
    * TODO: Holdings-to-dictionary behaviour
    """

    def test_initial_settings_for_default_portfolio(self):
        """
        Test that the initial settings are as they should be
        for two specified portfolios.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)

        # Test a default Portfolio
        port1 = Portfolio(start_dt)
        self.assertEqual(port1.start_dt, start_dt)
        self.assertEqual(port1.cur_dt, start_dt)
        self.assertEqual(port1.currency, "USD")
        self.assertEqual(port1.starting_cash, 0.0)
        self.assertEqual(port1.portfolio_id, None)
        self.assertEqual(port1.name, None)
        self.assertEqual(port1.total_securities_value, 0.0)
        self.assertEqual(port1.total_cash, 0.0)
        self.assertEqual(port1.total_equity, 0.0)

        # Test a Portfolio with keyword arguments
        port2 = Portfolio(
            start_dt, starting_cash=1234567.56, currency="USD",
            portfolio_id=12345, name="My Second Test Portfolio"
        )
        self.assertEqual(port2.start_dt, start_dt)
        self.assertEqual(port2.cur_dt, start_dt)
        self.assertEqual(port2.currency, "USD")
        self.assertEqual(port2.starting_cash, 1234567.56)
        self.assertEqual(port2.portfolio_id, 12345)
        self.assertEqual(port2.name, "My Second Test Portfolio")
        self.assertEqual(port2.total_equity, 1234567.56)
        self.assertEqual(port2.total_securities_value, 0.0)
        self.assertEqual(port2.total_cash, 1234567.56)

    def test_portfolio_currency_settings(self):
        """
        Test that USD and GBP currencies are correctly set with
        some currency keyword arguments and that the currency
        formatter produces the correct strings.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        cash = 1234567.56

        # Test a US portfolio produces correct values
        cur1 = "USD"
        port1 = Portfolio(start_dt, currency=cur1)
        self.assertEqual(port1.currency, "USD")
        self.assertEqual(port1._currency_format(cash), "$1,234,567.56")

        # Test a UK portfolio produces correct values
        cur2 = "GBP"
        port2 = Portfolio(start_dt, currency=cur2)
        self.assertEqual(port2.currency, "GBP")
        self.assertEqual(port2._currency_format(cash), "£1,234,567.56")

        # Test a German portfolio fails (DE not supported yet)
        cur3 = "DE"
        with self.assertRaises(PortfolioException):
            Portfolio(start_dt, currency=cur3)

    def test_subscribe_funds_behaviour(self):
        """
        Test subscribe_funds raises for incorrect datetime
        Test subscribe_funds raises for negative amount
        Test subscribe_funds correctly adds positive
        amount, generates correct event and modifies time
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        earlier_dt = pd.Timestamp('2017-10-04 08:00:00', tz=pytz.UTC)
        later_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
        pos_cash = 1000.0
        neg_cash = -1000.0
        port = Portfolio(start_dt)

        # Test subscribe_funds raises for incorrect datetime
        with self.assertRaises(PortfolioException):
            port.subscribe_funds(earlier_dt, pos_cash)

        # Test subscribe_funds raises for negative amount
        with self.assertRaises(PortfolioException):
            port.subscribe_funds(start_dt, neg_cash)

        # Test subscribe_funds correctly adds positive
        # amount, generates correct event and modifies time
        port.subscribe_funds(later_dt, pos_cash)
        self.assertEqual(port.total_cash, 1000.0)
        self.assertEqual(port.total_securities_value, 0.0)
        self.assertEqual(port.total_equity, 1000.0)
        pe = PortfolioEvent(
            date=later_dt, type='subscription',
            description="SUBSCRIPTION", debit=0.0,
            credit=1000.0, balance=1000.0
        )
        self.assertEqual(port.history, [pe])
        self.assertEqual(port.cur_dt, later_dt)

    def test_withdraw_funds_behaviour(self):
        """
        Test withdraw_funds raises for incorrect datetime
        Test withdraw_funds raises for negative amount
        Test withdraw_funds raises for lack of cash
        Test withdraw_funds correctly subtracts positive
        amount, generates correct event and modifies time
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        earlier_dt = pd.Timestamp('2017-10-04 08:00:00', tz=pytz.UTC)
        later_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
        even_later_dt = pd.Timestamp('2017-10-07 08:00:00', tz=pytz.UTC)
        pos_cash = 1000.0
        neg_cash = -1000.0
        port_raise = Portfolio(start_dt)

        # Test withdraw_funds raises for incorrect datetime
        with self.assertRaises(PortfolioException):
            port_raise.withdraw_funds(earlier_dt, pos_cash)

        # Test withdraw_funds raises for negative amount
        with self.assertRaises(PortfolioException):
            port_raise.withdraw_funds(start_dt, neg_cash)

        # Test withdraw_funds raises for not enough cash
        port_broke = Portfolio(start_dt)
        port_broke.subscribe_funds(later_dt, 1000.0)
        with self.assertRaises(PortfolioException):
            port_broke.withdraw_funds(later_dt, 2000.0)

        # Test withdraw_funds correctly subtracts positive
        # amount, generates correct event and modifies time
        # Initial subscribe
        port_cor = Portfolio(start_dt)
        port_cor.subscribe_funds(later_dt, pos_cash)
        pe_sub = PortfolioEvent(
            date=later_dt, type='subscription',
            description="SUBSCRIPTION", debit=0.0,
            credit=1000.0, balance=1000.0
        )
        self.assertEqual(port_cor.total_cash, 1000.0)
        self.assertEqual(port_cor.total_securities_value, 0.0)
        self.assertEqual(port_cor.total_equity, 1000.0)
        self.assertEqual(port_cor.history, [pe_sub])
        self.assertEqual(port_cor.cur_dt, later_dt)
        # Now withdraw
        port_cor.withdraw_funds(even_later_dt, 468.0)
        pe_wdr = PortfolioEvent(
            date=even_later_dt, type='withdrawal',
            description="WITHDRAWAL", debit=468.0,
            credit=0.0, balance=532.0
        )
        self.assertEqual(port_cor.total_cash, 532.0)
        self.assertEqual(port_cor.total_securities_value, 0.0)
        self.assertEqual(port_cor.total_equity, 532.0)
        self.assertEqual(port_cor.history, [pe_sub, pe_wdr])
        self.assertEqual(port_cor.cur_dt, even_later_dt)

    def test_transact_asset_behaviour(self):
        """
        Test transact_asset raises for incorrect time
        Test transact_asset raises for transaction total
        cost exceeding total cash
        Test correct total_cash and total_securities_value
        for correct transaction (commission etc), correct
        portfolio event and correct time update
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        earlier_dt = pd.Timestamp('2017-10-04 08:00:00', tz=pytz.UTC)
        later_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
        even_later_dt = pd.Timestamp('2017-10-07 08:00:00', tz=pytz.UTC)
        port = Portfolio(start_dt)
        asset = EquityMock("Acme Inc.", "AAA", "NYSE", tax_exempt=False)

        # Test transact_asset raises for incorrect time
        tn_early = Transaction(
            asset=asset,
            quantity=100,
            dt=earlier_dt,
            price=567.0,
            order_id=1,
            commission=0.0
        )
        with self.assertRaises(PortfolioException):
            port.transact_asset(tn_early)

        # Test transact_asset raises for transaction total
        # cost exceeding total cash
        port.subscribe_funds(later_dt, 1000.0)
        self.assertEqual(port.total_cash, 1000.0)
        self.assertEqual(port.total_securities_value, 0.0)
        self.assertEqual(port.total_equity, 1000.0)
        pe_sub1 = PortfolioEvent(
            date=later_dt, type='subscription',
            description="SUBSCRIPTION", debit=0.0,
            credit=1000.0, balance=1000.0
        )
        tn_large = Transaction(
            asset=asset,
            quantity=100,
            dt=later_dt,
            price=567.0,
            order_id=1,
            commission=15.78
        )
        with self.assertRaises(PortfolioException):
            port.transact_asset(tn_large)

        # Test correct total_cash and total_securities_value
        # for correct transaction (commission etc), correct
        # portfolio event and correct time update
        port.subscribe_funds(even_later_dt, 99000.0)
        self.assertEqual(port.total_cash, 100000.0)
        self.assertEqual(port.total_securities_value, 0.0)
        self.assertEqual(port.total_equity, 100000.0)
        pe_sub2 = PortfolioEvent(
            date=even_later_dt, type='subscription',
            description="SUBSCRIPTION", debit=0.0,
            credit=99000.0, balance=100000.0
        )
        tn_even_later = Transaction(
            asset=asset,
            quantity=100,
            dt=even_later_dt,
            price=567.0,
            order_id=1,
            commission=15.78
        )
        port.transact_asset(tn_even_later)
        self.assertEqual(port.total_cash, 43284.22)
        self.assertEqual(port.total_securities_value, 56700.00)
        self.assertEqual(port.total_equity, 99984.22)
        description = "LONG 100 ACME INC. 567.00 07/10/2017"
        pe_tn = PortfolioEvent(
            date=even_later_dt, type="asset_transaction",
            description=description, debit=56715.78,
            credit=0.0, balance=43284.22
        )
        self.assertEqual(port.history, [pe_sub1, pe_sub2, pe_tn])
        self.assertEqual(port.cur_dt, even_later_dt)

    def test_cash_dividend_behaviour(self):
        """
        Test cash_dividend raises for incorrect datetime
        Test cash_dividend raises for asset not being in portfolio
        Test cash_dividend raises if div_per_share is negative
        Test cash_dividend for multiple rounding cases, portfolio
        events and updated times
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        earlier_dt = pd.Timestamp('2017-10-04 08:00:00', tz=pytz.UTC)
        later_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
        even_later_dt = pd.Timestamp('2017-10-07 08:00:00', tz=pytz.UTC)
        much_later_dt = pd.Timestamp('2017-11-07 08:00:00', tz=pytz.UTC)
        asset = EquityMock("Acme Inc.", "AAA", "NYSE", tax_exempt=False)
        port = Portfolio(start_dt)

        # Test cash_dividend raises for incorrect datetime
        with self.assertRaises(PortfolioException):
            port.cash_dividend(earlier_dt, asset, 0.3567)

        # Test cash_dividend raises for asset not being in portfolio
        with self.assertRaises(PortfolioException):
            port.cash_dividend(later_dt, asset, 0.3567)

        # Test cash_dividend raises if div_per_share is negative
        port.subscribe_funds(later_dt, 100000.0)
        pe_sub = PortfolioEvent(
            date=later_dt, type='subscription',
            description="SUBSCRIPTION", debit=0.0,
            credit=100000.0, balance=100000.0
        )
        tn_asset = Transaction(
            asset=asset,
            quantity=100,
            dt=later_dt,
            price=567.0,
            order_id=1,
            commission=15.78
        )
        port.transact_asset(tn_asset)
        description = "LONG 100 ACME INC. 567.00 06/10/2017"
        pe_tn = PortfolioEvent(
            date=later_dt, type="asset_transaction",
            description=description, debit=56715.78,
            credit=0.0, balance=43284.22
        )
        with self.assertRaises(PortfolioException):
            port.cash_dividend(even_later_dt, asset, -0.3567)

        # Test cash_dividend for multiple rounding cases, portfolio
        # events and updated times
        # Dividend #1
        port.cash_dividend(even_later_dt, asset, 0.3567)
        description = "DIVIDEND 100 ACME INC. 0.36USD 07/10/2017"
        pe_div1 = PortfolioEvent(
            date=even_later_dt, type='dividend',
            description=description,
            debit=0.0, credit=35.67,
            balance=43319.89
        )
        self.assertEqual(port.total_cash, 43319.89)
        self.assertEqual(port.total_securities_value, 56700.00)
        self.assertEqual(port.total_equity, 100019.89)
        self.assertEqual(port.cur_dt, even_later_dt)
        # Dividend #2
        port.cash_dividend(much_later_dt, asset, 0.42538)
        description = "DIVIDEND 100 ACME INC. 0.43USD 07/11/2017"
        pe_div2 = PortfolioEvent(
            date=much_later_dt, type='dividend',
            description=description,
            debit=0.0, credit=42.53,
            balance=43362.42
        )
        self.assertEqual(port.total_cash, 43362.42)
        self.assertEqual(port.total_securities_value, 56700.00)
        self.assertEqual(port.total_equity, 100062.42)
        self.assertEqual(port.history, [pe_sub, pe_tn, pe_div1, pe_div2])
        self.assertEqual(port.cur_dt, much_later_dt)

    def test_update_market_value_of_asset_not_in_list(self):
        """
        Test update_market_value_of_asset for asset not in list.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        later_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
        port = Portfolio(start_dt)
        asset = EquityMock("Acme Inc.", "AAA", "NYSE", tax_exempt=False)
        update = port.update_market_value_of_asset(
            asset, 54.34, later_dt
        )
        self.assertEqual(update, None)

    def test_update_market_value_of_asset_negative_price(self):
        """
        Test update_market_value_of_asset for
        asset with negative price.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        later_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
        port = Portfolio(start_dt)

        asset = EquityMock("Acme Inc.", "AAA", "NYSE", tax_exempt=False)
        port.subscribe_funds(later_dt, 100000.0)
        tn_asset = Transaction(
            asset=asset,
            quantity=100,
            dt=later_dt,
            price=567.0,
            order_id=1,
            commission=15.78
        )
        port.transact_asset(tn_asset)
        with self.assertRaises(PortfolioException):
            port.update_market_value_of_asset(
                asset, -54.34, later_dt
            )

    def test_update_market_value_of_asset_earlier_date(self):
        """
        Test update_market_value_of_asset for asset
        with current_trade_date in past
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        earlier_dt = pd.Timestamp('2017-10-04 08:00:00', tz=pytz.UTC)
        later_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
        port = Portfolio(start_dt)

        asset = EquityMock("Acme Inc.", "AAA", "NYSE", tax_exempt=False)
        port.subscribe_funds(later_dt, 100000.0)
        tn_asset = Transaction(
            asset=asset,
            quantity=100,
            dt=later_dt,
            price=567.0,
            order_id=1,
            commission=15.78
        )
        port.transact_asset(tn_asset)
        with self.assertRaises(PortfolioException):
            port.update_market_value_of_asset(
                asset, 50.23, earlier_dt
            )

    def test_history_to_df_empty(self):
        """
        Test 'history_to_df' with no events.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        port = Portfolio(start_dt)
        hist_df = port.history_to_df()
        test_df = pd.DataFrame(
            [], columns=[
                "date", "type", "description",
                "debit", "credit", "balance"
            ]
        )
        test_df.set_index(keys=["date"], inplace=True)
        self.assertEqual(
            sorted(test_df.columns),
            sorted(hist_df.columns)
        )
        self.assertEqual(len(test_df), len(hist_df))
        self.assertEqual(len(hist_df), 0)

    def test_holdings_to_dict_for_no_holdings(self):
        """
        Test holdings_to_dict for no holdings.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        port = Portfolio(start_dt)
        self.assertEqual(port.holdings_to_dict(), {})

    def test_holdings_to_dict_for_two_holdings(self):
        """
        Test holdings_to_dict for two holdings.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        asset1_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
        asset2_dt = pd.Timestamp('2017-10-07 08:00:00', tz=pytz.UTC)
        update_dt = pd.Timestamp('2017-10-08 08:00:00', tz=pytz.UTC)
        asset1 = EquityMock("AAA Inc.", "AAA", "NYSE", tax_exempt=False)
        asset2 = EquityMock("BBB Inc.", "BBB", "NYSE", tax_exempt=False)
        port = Portfolio(start_dt)
        port.subscribe_funds(start_dt, 100000.0)
        tn_asset1 = Transaction(
            asset=asset1, quantity=100, dt=asset1_dt,
            price=567.0, order_id=1, commission=15.78
        )
        port.transact_asset(tn_asset1)
        tn_asset2 = Transaction(
            asset=asset2, quantity=100, dt=asset2_dt,
            price=123.0, order_id=2, commission=7.64
        )
        port.transact_asset(tn_asset2)
        port.update_market_value_of_asset(asset2, 134.0, update_dt)
        test_holdings = {
            asset1: {
                "quantity": 100,
                "book_cost": 56715.78,
                "market_value": 56700.0,
                "gain": -15.78,
                "perc_gain": -0.027822944513854874
            },
            asset2: {
                "quantity": 100,
                "book_cost": 12307.64,
                "market_value": 13400.0,
                "gain": 1092.3600000000006,
                "perc_gain": 8.8754627207165679
            }
        }
        port_holdings = port.holdings_to_dict()
        # This is needed because we're not using Decimal
        # datatypes and have to compare slightly differing
        # floating point representations
        for asset in (asset1, asset2):
            for key, val in test_holdings[asset].items():
                self.assertAlmostEqual(
                    port_holdings[asset][key],
                    test_holdings[asset][key]
                )

    def test_portfolio_to_dict_empty_portfolio(self):
        """
        Test 'portfolio_to_dict' method for an empty Portfolio.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        port = Portfolio(start_dt)
        port.subscribe_funds(start_dt, 100000.0)
        port_dict = port.portfolio_to_dict()
        test_dict = {
            "total_cash": 100000.0,
            "total_securities_value": 0.0,
            "total_equity": 100000.0
        }
        self.assertEqual(port_dict, test_dict)

    def test_holdings_to_console_for_empty_portfolio(self):
        """
        Tests the 'holdings_to_console' console output for
        an empty Portfolio.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        port = Portfolio(start_dt)
        test_str = "\x1b[1;36m\nPortfolio Holdings | None - None\n\n" \
            "\x1b[0m*======================================================" \
            "============================================*\n" \
            "| Holding | Quantity | Price | Change |      Book Cost " \
            "|   Market Value |      Unrealised Gain     | \n" \
            "*======================================================" \
            "============================================*\n" \
            "*======================================================" \
            "============================================*\n" \
            "|   Total |                           |          $0.00 " \
            "|          $0.00 |         \x1b[1;37m$0.00\x1b[0m      " \
            "\x1b[1;37m0.00%\x1b[0m |\n" \
            "*======================================================" \
            "============================================*"
        with captured_output() as (out, err):
            port.holdings_to_console()
        output = out.getvalue().strip()
        self.assertEqual(test_str, output)

    def test_holdings_to_console_for_two_positions(self):
        """
        Tests the 'holdings_to_console' console output for
        two Position entities within the Portfolio.
        """
        start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
        asset1_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
        asset2_dt = pd.Timestamp('2017-10-07 08:00:00', tz=pytz.UTC)
        update_dt = pd.Timestamp('2017-10-08 08:00:00', tz=pytz.UTC)
        asset1 = EquityMock("AAA Inc.", "AAA", "NYSE", tax_exempt=False)
        asset2 = EquityMock("BBB Inc.", "BBB", "NYSE", tax_exempt=False)
        port = Portfolio(start_dt)
        port.subscribe_funds(start_dt, 100000.0)
        tn_asset1 = Transaction(
            asset=asset1, quantity=100, dt=asset1_dt,
            price=567.0, order_id=1, commission=15.78
        )
        port.transact_asset(tn_asset1)
        tn_asset2 = Transaction(
            asset=asset2, quantity=100, dt=asset2_dt,
            price=123.0, order_id=2, commission=7.64
        )
        port.transact_asset(tn_asset2)
        test_str = "\x1b[1;36m\nPortfolio Holdings | None - None\n\n" \
            "\x1b[0m*======================================================" \
            "============================================*\n" \
            "| Holding | Quantity | Price | Change |      Book Cost " \
            "|   Market Value |      Unrealised Gain     | \n" \
            "*======================================================" \
            "============================================*\n" \
            "|     AAA |      100 |     - |      - |     $56,715.78 " \
            "|     $56,700.00 |       \x1b[1;31m-$15.78\x1b[0m     " \
            "\x1b[1;31m-0.03%\x1b[0m |\n|     BBB |      100 |     - |" \
            "      - |     $12,307.64 " \
            "|     $12,300.00 |        \x1b[1;31m-$7.64\x1b[0m     " \
            "\x1b[1;31m-0.06%\x1b[0m |\n" \
            "*======================================================" \
            "============================================*\n" \
            "|   Total |                           |     $69,023.42 " \
            "|     $69,000.00 |       \x1b[1;31m-$23.42\x1b[0m     " \
            "\x1b[1;31m-0.03%\x1b[0m |\n" \
            "*======================================================" \
            "============================================*"
        with captured_output() as (out, err):
            port.holdings_to_console()
        output = out.getvalue().strip()
        self.assertEqual(test_str, output)

        port.update_market_value_of_asset(asset2, 134.0, update_dt)
        test_str = "\x1b[1;36m\nPortfolio Holdings | None - None\n\n" \
            "\x1b[0m*======================================================" \
            "============================================*\n" \
            "| Holding | Quantity | Price | Change |      Book Cost " \
            "|   Market Value |      Unrealised Gain     | \n" \
            "*======================================================" \
            "============================================*\n" \
            "|     AAA |      100 |     - |      - |     $56,715.78 " \
            "|     $56,700.00 |       \x1b[1;31m-$15.78\x1b[0m     " \
            "\x1b[1;31m-0.03%\x1b[0m |\n|     BBB |      100 |     - |" \
            "      - |     $12,307.64 " \
            "|     $13,400.00 |     \x1b[1;32m$1,092.36\x1b[0m     " \
            " \x1b[1;32m8.88%\x1b[0m |\n" \
            "*======================================================" \
            "============================================*\n" \
            "|   Total |                           |     $69,023.42 " \
            "|     $70,100.00 |     \x1b[1;32m$1,076.58\x1b[0m     " \
            " \x1b[1;32m1.56%\x1b[0m |\n" \
            "*======================================================" \
            "============================================*"
        with captured_output() as (out, err):
            port.holdings_to_console()
        output = out.getvalue().strip()
        self.assertEqual(test_str, output)


if __name__ == "__main__":
    unittest.main()
