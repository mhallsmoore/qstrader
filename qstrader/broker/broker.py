from abc import ABCMeta, abstractmethod


class Broker(object):
    """
    This abstract class provides an interface to a
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

    The Broker can execute orders. It contains a queue of
    open orders, needed for handling closed market situations.

    The Broker also supports individual history events for each
    sub-portfolio, which can be aggregated, along with the
    account history, to produce a full trading history for the
    account.
    """

    __metaclass__ = ABCMeta

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
    def get_account_total_non_cash_equity(self):
        raise NotImplementedError(
            "Should implement get_account_total_non_cash_equity()"
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
    def get_portfolio_total_non_cash_equity(self, portfolio_id):
        raise NotImplementedError(
            "Should implement get_portfolio_total_non_cash_equity()"
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
    def submit_order(self, portfolio_id, order):
        raise NotImplementedError(
            "Should implement submit_order()"
        )
