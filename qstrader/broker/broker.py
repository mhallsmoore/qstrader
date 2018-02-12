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

from abc import ABCMeta, abstractmethod


class BrokerException(Exception):
    pass


class Broker(object):
    """This abstract class provides an interface to a
    generic broker entity. Both simulated and live brokers
    will be derived from this ABC. This ensures that trading
    algorithm specific logic is completely identical for both
    simulated and live environments.

    The Broker has an associated master denominated currency
    through which all subscriptions and withdrawals will occur.

    The Broker entity can support multiple sub-portfolios, each
    with their own separate handling of PnL. The individual PnLs
    from each sub-portfolio can be aggregated to generate an
    account-wide PnL.

    The Broker can execute orders against an Exchange and also
    contains a queue of open orders (such as limit orders).
    Open orders can be queried or cancelled.

    The Broker provides a latest asset price for each Asset in
    the form of a bid/ask spread. For data sources that only
    provide a mid-point, the bid/ask will be identical in each.

    The Broker also supports individual history events for each
    sub-portfolio, which can be aggregated, along with the
    account history, to produce a full trading history for the
    account.
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def subscribe_funds_to_account(self, amount):
        raise NotImplementedError(
            "Should implement subscribe_funds_to_account()"
        )

    @abstractmethod
    def withdraw_funds_from_account(self, amount):
        raise NotImplementedError(
            "Should implement withdraw_funds_from_account()"
        )

    @abstractmethod
    def get_account_cash_balance(self, currency=None):
        raise NotImplementedError(
            "Should implement get_account_cash_balance()"
        )

    @abstractmethod
    def get_account_total_market_value(self):
        raise NotImplementedError(
            "Should implement get_account_total_market_value()"
        )

    @abstractmethod
    def get_account_total_equity(self):
        raise NotImplementedError(
            "Should implement get_account_total_equity()"
        )

    @abstractmethod
    def create_portfolio(self, portfolio_id, name):
        raise NotImplementedError(
            "Should implement create_portfolio()"
        )

    @abstractmethod
    def list_all_portfolios(self):
        raise NotImplementedError(
            "Should implement list_all_portfolios()"
        )

    @abstractmethod
    def subscribe_funds_to_portfolio(self, portfolio_id, amount):
        raise NotImplementedError(
            "Should implement subscribe_funds_to_portfolio()"
        )

    @abstractmethod
    def withdraw_funds_from_portfolio(self, portfolio_id, amount):
        raise NotImplementedError(
            "Should implement withdraw_funds_from_portfolio()"
        )

    @abstractmethod
    def get_portfolio_cash_balance(self, portfolio_id):
        raise NotImplementedError(
            "Should implement get_portfolio_cash_balance()"
        )

    @abstractmethod
    def get_portfolio_total_market_value(self, portfolio_id):
        raise NotImplementedError(
            "Should implement get_portfolio_total_market_value()"
        )

    @abstractmethod
    def get_portfolio_total_equity(self, portfolio_id):
        raise NotImplementedError(
            "Should implement get_portfolio_total_equity()"
        )

    @abstractmethod
    def get_portfolio_as_dict(self, portfolio_id):
        raise NotImplementedError(
            "Should implement get_portfolio_as_dict()"
        )

    @abstractmethod
    def get_latest_asset_price(self, asset):
        raise NotImplementedError(
            "Should implement get_latest_asset_price()"
        )

    @abstractmethod
    def submit_order(self, portfolio_id, order):
        raise NotImplementedError(
            "Should implement submit_order()"
        )
