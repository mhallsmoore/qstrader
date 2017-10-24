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

import pandas as pd

from qstrader.broker.broker import Broker, BrokerException
from qstrader.broker.broker_commission import BrokerCommission
from qstrader.broker.zero_broker_commission import ZeroBrokerCommission
import qstrader.settings


class SimulatedBroker(Broker):
    """A class to handle simulation of a brokerage that
    provides sensible defaults for both currency (USD) and
    transaction cost handling for execution.

    The default transaction costs do not include slippage
    or market impact but do take into account commission.

    The default commission model is a ZeroBrokerCommission
    that charges no commission or tax (stamp duty).

    Parameters
    ----------
    start_dt : Pandas Timestamp
        The starting datetime of the account
    exchange : Exchange
        The simulated exchange entity which provides
        asset prices and an execution venue.
    account_id : str, optional
        The account ID for the brokerage account.
    currency : str, optional
        The currency denomination of the brokerage account.
    initial_funds : float, optional
        An initial amount of cash to add to the broker account.
    broker_commission : BrokerCommission, optional
        The transaction cost class for handling broker
        commission.
    """

    def __init__(
        self, start_dt, exchange,
        account_id=None, currency="USD",
        initial_funds=0.0, broker_commission=None
    ):
        self.start_dt = start_dt
        self.exchange = exchange
        self.account_id = account_id
        self.currency = self._set_base_currency(currency)
        self.initial_funds = self._set_initial_funds(initial_funds)
        self.broker_commission = self._set_broker_commission(
            broker_commission
        )
        self.cash_balances = self._set_cash_balances()
        self.portfolios = self._set_initial_portfolios()
        self.open_orders = self._set_initial_open_orders()

    def _set_base_currency(self, currency):
        """
        Check and set the base currency from a list of
        allowed currencies. Raise BrokerException if the
        currency is currently not supported by QSTrader.
        """
        if currency not in settings.CURRENCIES:
            raise BrokerException(
                "Currency '%s' is not supported by QSTrader. Could not "
                "set the base currency in the SimulatedBroker "
                "entity." % currency
            )
        else:
            return currency

    def _set_initial_funds(self, initial_funds):
        """
        Check and set the initial funds for the broker
        master account. Raise BrokerException if the
        amount is negative.
        """
        if initial_funds < 0.0:
            raise BrokerException(
                "Could not create the SimulatedBroker entity as the "
                "provided initial funds of '%s' were "
                "negative." % initial_funds
            )
        else:
            return initial_funds

    def _set_broker_commission(self, broker_commission):
        """
        Check and set the BrokerCommission instance for
        the broker. The class default is no commission.
        """
        if broker_commission is None:
            return ZeroBrokerCommission()
        else:
            if issubclass(broker_commission, BrokerCommission):
                return broker_commission()
            else:
                raise BrokerException(
                    "Provided broker commission is not a "
                    "BrokerCommission subclass, so could not "
                    "create the Broker entity."
                )

    def _set_cash_balances(self):
        """
        Set the appropriate cash balances in the various
        supported currencies, depending upon the availability
        of initial funds.
        """
        pass

    def _set_initial_portfolios(self):
        """
        Set the appropriate initial portfolios dictionary.
        """
        return {}

    def _set_initial_open_orders(self):
        """
        Set the appropriate initial open orders dictionary.
        """
        return {}

    def subscribe_funds_to_account(self, amount):
        """
        Subscribe an amount of cash in the base currency
        to the broker master cash account.
        """
        pass

    def withdraw_funds_from_account(self, amount):
        """
        Withdraws an amount of cash in the base currency
        from the broker master cash account, assuming an
        amount equal to or more cash is present. If less
        cash is present, a BrokerException is raised.
        """
        pass

    def get_account_cash_balance(self, currency=None):
        """
        Retrieve the cash dictionary of the account, or
        if a currency is provided, the cash value itself.
        Raises a BrokerException if the currency is not
        found within the currency cash dictionary.
        """
        pass

    def get_account_total_pnl(self):
        """
        Retrieve the total summarised PnL and cash balances
        for the broker account, in a dictionary format, with
        'cash' and portfolio_ids as keys.
        """
        pass

    def get_account_history(self):
        """
        Retrieve the history of the entire account including
        all sub-portfolio history, aggregated to date, as a
        list of PortfolioEvent and AccountEvent entities.
        """
        pass

    def get_account_history_as_df(self):
        """
        Retrieve the history of the entire account including
        all sub-portfolio history, aggregated to date, as a
        Pandas DataFrame.
        """
        pass

    def create_portfolio(self, portfolio_id, name=None):
        """
        Create a new sub-portfolio with ID 'portfolio_id' and
        an optional name given by 'name'.
        """
        pass

    def list_all_portfolios(self):
        """
        List all of the sub-portfolios associated with this
        broker account.
        """
        pass

    def subscribe_funds_to_portfolio(self, portfolio_id, amount):
        """
        Subscribe funds to a particular sub-portfolio, assuming
        it exists and the cash amount is positive. Otherwise raise
        a BrokerException.
        """
        pass

    def withdraw_funds_from_portfolio(self, portfolio_id, amount):
        """
        Withdraw funds from a particular sub-portfolio, assuming
        it exists, the cash amount is positive and there is
        sufficient remaining cash in the sub-portfolio to
        withdraw. Otherwise raise a BrokerException.
        """
        pass

    def get_portfolio_cash_balance(self, portfolio_id):
        """
        Retrieve the cash balance of a sub-portfolio, if
        it exists. Otherwise raise a BrokerException.
        """
        pass

    def get_portfolio_total_pnl(self, portfolio_id):
        """
        Retrieve the total PnL of the sub-portfolio to
        date, including cash balance, if the sub-portfolio
        exists.
        """
        pass

    def get_portfolio_history(self, portfolio_id):
        """
        Retrieve a list of PortfolioEvent entities for a
        particular sub-portfolio, assuming it exists.
        Otherwise raise a BrokerException.
        """
        pass

    def get_portfolio_history_as_df(self, portfolio_id):
        """
        Retrieve a Pandas DataFrame of the sub-portfolio
        history, assuming the sub-portfolio exists.
        Otherwise raise a BrokerException.
        """
        pass

    def get_latest_asset_price(self, asset):
        """
        Retrieve the latest bid/ask price provided by the
        broker for a particular asset, as a tuple (bid, ask).

        If the broker cannot provide a price then a tuple
        of (None, None) is returned.

        If the broker only has access to the mid-price of
        an asset, then the same value will fill both tuple
        entries: (price, price).
        """
        pass

    def execute_order(self, portfolio_id, order):
        """
        Execute an Order instance against the sub-portfolio
        with ID 'portfolio_id'. For the SimulatedBroker class
        specifically there are no restrictions on this occuring
        beyond having sufficient cash in the sub-portfolio to
        allow this to occur.

        This does not take into settlement dates, as with most
        brokerage accounts. The cash is taken immediately upon
        entering a long position and returned immediately upon
        closing out the position.

        The Order entities are added to the open_orders dictionary,
        with sub_portfolio IDs as keys, and collections.deque
        double-ended queue structures as values, if they cannot be
        executed immediately (i.e. limit order/stop order).
        """
        pass

    def get_all_open_orders(self, portfolio_id=None):
        """
        Retrieves the dictionary of sub-portfolios, each with
        the list of current open orders. If a sub-portfolio ID
        is specifically provided, only the open orders associated
        with that account are returned (assuming it exists).
        """
        pass

    def cancel_open_order(self, order_id):
        """
        Cancels an open order via its order_id.
        """
        pass

    def cancel_all_open_orders(self, portfolio_id=None):
        """
        Cancels all open orders in the account or only those for
        a specific portfolio if an ID is provided and it exists.
        """
        pass
