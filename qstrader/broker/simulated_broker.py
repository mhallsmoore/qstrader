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

import numpy as np

from qstrader.broker.broker import Broker, BrokerException
from qstrader.broker.broker_commission import BrokerCommission
from qstrader.broker.portfolio import Portfolio
from qstrader.broker.transaction import Transaction
from qstrader.broker.zero_broker_commission import ZeroBrokerCommission
from qstrader.exchange.exchange import ExchangeException
from qstrader import settings


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
    base_currency : str, optional
        The currency denomination of the brokerage account.
    initial_funds : float, optional
        An initial amount of cash to add to the broker account.
    broker_commission : BrokerCommission, optional
        The transaction cost class for handling broker
        commission.
    """

    def __init__(
        self, start_dt, exchange,
        account_id=None, base_currency="USD",
        initial_funds=0.0, broker_commission=None
    ):
        self.start_dt = start_dt
        self.cur_dt = start_dt
        self.exchange = exchange
        self.account_id = account_id
        self.base_currency = self._set_base_currency(base_currency)
        self.initial_funds = self._set_initial_funds(initial_funds)
        self.broker_commission = self._set_broker_commission(
            broker_commission
        )
        self.cash_balances = self._set_cash_balances()
        self.portfolios = self._set_initial_portfolios()
        self.open_orders = self._set_initial_open_orders()

    def _set_base_currency(self, base_currency):
        """
        Check and set the base currency from a list of
        allowed currencies. Raise BrokerException if the
        currency is currently not supported by QSTrader.
        """
        if base_currency not in settings.CURRENCIES:
            raise BrokerException(
                "Currency '%s' is not supported by QSTrader. Could not "
                "set the base currency in the SimulatedBroker "
                "entity." % base_currency
            )
        else:
            return base_currency

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
            if (
                hasattr(broker_commission, "__class__") and
                hasattr(broker_commission.__class__, "__name__") and
                issubclass(broker_commission.__class__, BrokerCommission)
            ):
                return broker_commission
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
        cash_dict = dict(
            (currency, 0.0)
            for currency in settings.CURRENCIES
        )
        if self.initial_funds > 0.0:
            cash_dict[self.base_currency] = self.initial_funds
        return cash_dict

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
        if amount < 0.0:
            raise BrokerException(
                "Cannot credit negative amount: "
                "'%s' to the broker account." % amount
            )
        self.cash_balances[self.base_currency] += amount

    def withdraw_funds_from_account(self, amount):
        """
        Withdraws an amount of cash in the base currency
        from the broker master cash account, assuming an
        amount equal to or more cash is present. If less
        cash is present, a BrokerException is raised.
        """
        if amount < 0:
            raise BrokerException(
                "Cannot debit negative amount: "
                "'%s' from the broker account." % amount
            )
        if amount > self.cash_balances[self.base_currency]:
            raise BrokerException(
                "Not enough cash in the broker account to "
                "withdraw. %0.2f withdrawal request exceeds "
                "current broker account cash balance of %0.2f." % (
                    amount, self.cash_balances[self.base_currency]
                )
            )
        self.cash_balances[self.base_currency] -= amount

    def get_account_cash_balance(self, currency=None):
        """
        Retrieve the cash dictionary of the account, or
        if a currency is provided, the cash value itself.
        Raises a BrokerException if the currency is not
        found within the currency cash dictionary.
        """
        if currency is None:
            return self.cash_balances
        if currency not in self.cash_balances.keys():
            raise BrokerException(
                "Currency of type '%s' is not found within the "
                "broker cash master accounts. Could not retrieve "
                "cash balance." % currency
            )
        return self.cash_balances[currency]

    def get_account_total_market_value(self):
        """
        Retrieve the total market value of the account, across
        each portfolio.
        """
        tmv_dict = {}
        master_tmv = 0.0
        for portfolio in self.portfolios.values():
            pmv = self.get_portfolio_total_market_value(
                portfolio.portfolio_id
            )
            tmv_dict[portfolio.portfolio_id] = pmv
            master_tmv += pmv
        tmv_dict["master"] = master_tmv
        return tmv_dict

    def create_portfolio(self, portfolio_id, name=None):
        """
        Create a new sub-portfolio with ID 'portfolio_id' and
        an optional name given by 'name'.
        """
        portfolio_id_str = str(portfolio_id)
        if portfolio_id_str in self.portfolios.keys():
            raise BrokerException(
                "Portfolio with ID '%s' already exists. Cannot create "
                "second portfolio with the same ID." % portfolio_id_str
            )
        else:
            p = Portfolio(
                self.cur_dt,
                currency=self.base_currency,
                portfolio_id=portfolio_id_str,
                name=name
            )
            self.portfolios[portfolio_id_str] = p
            self.open_orders[portfolio_id_str] = collections.deque()

    def list_all_portfolios(self):
        """
        List all of the sub-portfolios associated with this
        broker account in order of portfolio ID.
        """
        if self.portfolios == {}:
            return []
        return sorted(
            list(self.portfolios.values()),
            key=lambda port: port.portfolio_id
        )

    def subscribe_funds_to_portfolio(self, portfolio_id, amount):
        """
        Subscribe funds to a particular sub-portfolio, assuming
        it exists and the cash amount is positive. Otherwise raise
        a BrokerException.
        """
        if amount < 0.0:
            raise BrokerException(
                "Cannot add negative amount: "
                "%0.2f to a portfolio account." % amount
            )
        if portfolio_id not in self.portfolios.keys():
            raise BrokerException(
                "Portfolio with ID '%s' does not exist. Cannot subscribe "
                "funds to a non-existent portfolio." % portfolio_id
            )
        if amount > self.cash_balances[self.base_currency]:
            raise BrokerException(
                "Not enough cash in the broker master account to "
                "fund portfolio '%s'. %0.2f subscription amount exceeds "
                "current broker account cash balance of %0.2f." % (
                    portfolio_id, amount,
                    self.cash_balances[self.base_currency]
                )
            )
        self.portfolios[portfolio_id].subscribe_funds(self.cur_dt, amount)
        self.cash_balances[self.base_currency] -= amount

    def withdraw_funds_from_portfolio(self, portfolio_id, amount):
        """
        Withdraw funds from a particular sub-portfolio, assuming
        it exists, the cash amount is positive and there is
        sufficient remaining cash in the sub-portfolio to
        withdraw. Otherwise raise a BrokerException.
        """
        if amount < 0.0:
            raise BrokerException(
                "Cannot withdraw negative amount: "
                "%0.2f from a portfolio account." % amount
            )
        if portfolio_id not in self.portfolios.keys():
            raise BrokerException(
                "Portfolio with ID '%s' does not exist. Cannot "
                "withdraw funds from a non-existent "
                "portfolio. " % portfolio_id
            )
        if amount > self.portfolios[portfolio_id].total_cash:
            raise BrokerException(
                "Not enough cash in portfolio '%s' to withdraw "
                "into brokerage master account. Withdrawal "
                "amount %0.2f exceeds current portfolio cash "
                "balance of %0.2f." % (
                    portfolio_id, amount,
                    self.portfolios[portfolio_id].total_cash
                )
            )
        self.portfolios[portfolio_id].withdraw_funds(
            self.cur_dt, amount
        )
        self.cash_balances[self.base_currency] += amount

    def get_portfolio_cash_balance(self, portfolio_id):
        """
        Retrieve the cash balance of a sub-portfolio, if
        it exists. Otherwise raise a BrokerException.
        """
        if portfolio_id not in self.portfolios.keys():
            raise BrokerException(
                "Portfolio with ID '%s' does not exist. Cannot "
                "retrieve cash balance for non-existent "
                "portfolio." % portfolio_id
            )
        return self.portfolios[portfolio_id].total_cash

    def get_portfolio_total_market_value(self, portfolio_id):
        """
        Returns the current total market value of a Portfolio
        with ID 'portfolio_id'.
        """
        if portfolio_id not in self.portfolios.keys():
            raise BrokerException(
                "Portfolio with ID '%s' does not exist. "
                "Cannot return total market value for a "
                "non-existent portfolio." % portfolio_id
            )
        return self.portfolios[portfolio_id].total_value

    def get_portfolio_as_dict(self, portfolio_id):
        """
        Return a particular portfolio with ID 'portolio_id' as
        a dictionary with Asset objects as keys, with various
        attributes as sub-dictionaries. This includes 'quantity',
        'book_cost', 'market_value', 'gain' and 'perc_gain'.
        """
        if portfolio_id not in self.portfolios.keys():
            raise BrokerException(
                "Cannot return portfolio as dictionary since "
                "portfolio with ID '%s' does not exist." % portfolio_id
            )
        return self.portfolios[portfolio_id].portfolio_to_dict()

    def get_latest_asset_price(self, asset):
        """
        Retrieve the latest bid/ask price provided by the
        broker for a particular asset, as a tuple (bid, ask).

        If the broker cannot provide a price then a tuple
        of (np.NaN, np.NaN) is returned.

        If the broker only has access to the mid-price of
        an asset, then the same value will fill both tuple
        entries: (price, price).
        """
        try:
            bid_ask = self.exchange.get_latest_asset_bid_ask(asset)
        except ExchangeException:
            return (np.NaN, np.NaN)
        else:
            return bid_ask

    def submit_order(self, portfolio_id, order):
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
        """
        # Check that the portfolio actually exists
        if portfolio_id not in self.portfolios.keys():
            raise BrokerException(
                "Portfolio with ID '%s' does not exist. Order with "
                "ID '%s' was not executed." % (
                    portfolio_id, order.order_id
                )
            )

        # Obtain a price for the asset, if no price then
        # raise a BrokerException
        price_err_msg = "Could not obtain a latest market price for " \
            "Asset with ticker symbol '%s'. Order with ID '%s' was " \
            "not executed." % (
                order.asset.symbol, order.order_id
            )
        bid_ask = self.get_latest_asset_price(order.asset)
        if bid_ask == (np.NaN, np.NaN):
            raise BrokerException(price_err_msg)

        # Calculate the consideration and total commission
        # based on the commission model
        if order.direction > 0:
            price = bid_ask[1]
        else:
            price = bid_ask[0]
        consideration = round(price * order.quantity)
        total_commission = self.broker_commission.calc_total_cost(
            order.asset, consideration, self
        )

        # Create a transaction entity and update the portfolio
        txn = Transaction(
            order.asset, order.quantity, self.cur_dt,
            price, order.order_id, commission=total_commission
        )
        self.portfolios[portfolio_id].transact_asset(txn)

    def update(self, dt):
        """
        Updates the current SimulatedBroker timestamp
        """
        self.cur_dt = dt

        # Update portfolio asset values
        for portfolio in self.portfolios:
            for asset in self.portfolios[portfolio].pos_handler.positions:
                # TODO: Modify this to use bid/ask direction!
                price = self.get_latest_asset_price(asset)[0]
                self.portfolios[portfolio].update_market_value_of_asset(
                    asset, price, self.cur_dt
                )
            self.portfolios[portfolio].update(dt)
