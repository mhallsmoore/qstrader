import copy
import datetime
import logging

import pandas as pd

from qstrader import settings
from qstrader.broker.portfolio.portfolio_event import PortfolioEvent
from qstrader.broker.portfolio.position_handler import PositionHandler


class Portfolio(object):
    """
    Represents a portfolio of assets. It contains a cash
    account with the ability to subscribe and withdraw funds.
    It also contains a list of positions in assets, encapsulated
    by a PositionHandler instance.

    Parameters
    ----------
    start_dt : datetime
        Portfolio creation datetime.
    starting_cash : float, optional
        Starting cash of the portfolio. Defaults to 100,000 USD.
    currency: str, optional
        The portfolio denomination currency.
    portfolio_id: str, optional
        An identifier for the portfolio.
    name: str, optional
        The human-readable name of the portfolio.
    """

    def __init__(
        self,
        start_dt,
        starting_cash=0.0,
        currency="USD",
        portfolio_id=None,
        name=None
    ):
        """
        Initialise the Portfolio object with a PositionHandler,
        an event history, along with cash balance. Make sure
        the portfolio denomination currency is also set.
        """
        self.start_dt = start_dt
        self.current_dt = start_dt
        self.starting_cash = starting_cash
        self.currency = currency
        self.portfolio_id = portfolio_id
        self.name = name

        self.pos_handler = PositionHandler()
        self.history = []

        self.logger = logging.getLogger('Portfolio')
        self.logger.setLevel(logging.DEBUG)
        self.logger.info(
            '(%s) Portfolio "%s" instance initialised' % (
                self.current_dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                self.portfolio_id
            )
        )

        self._initialise_portfolio_with_cash()

    def _initialise_portfolio_with_cash(self):
        """
        Initialise the portfolio with a (default) currency Cash Asset
        with quantity equal to 'starting_cash'.
        """
        self.cash = copy.copy(self.starting_cash)

        if self.starting_cash > 0.0:
            self.history.append(
                PortfolioEvent.create_subscription(
                    self.current_dt, self.starting_cash, self.starting_cash
                )
            )

        self.logger.info(
            '(%s) Funds subscribed to portfolio "%s" '
            '- Credit: %0.2f, Balance: %0.2f' % (
                self.current_dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                self.portfolio_id,
                round(self.starting_cash, 2),
                round(self.starting_cash, 2)
            )
        )

    @property
    def total_market_value(self):
        """
        Obtain the total market value of the portfolio excluding cash.
        """
        return self.pos_handler.total_market_value()

    @property
    def total_equity(self):
        """
        Obtain the total market value of the portfolio including cash.
        """
        return self.total_market_value + self.cash

    @property
    def total_unrealised_pnl(self):
        """
        Calculate the sum of all the positions' unrealised P&Ls.
        """
        return self.pos_handler.total_unrealised_pnl()

    @property
    def total_realised_pnl(self):
        """
        Calculate the sum of all the positions' realised P&Ls.
        """
        return self.pos_handler.total_realised_pnl()

    @property
    def total_pnl(self):
        """
        Calculate the sum of all the positions' total P&Ls.
        """
        return self.pos_handler.total_pnl()

    def subscribe_funds(self, dt, amount):
        """
        Credit funds to the portfolio.
        """
        if dt < self.current_dt:
            raise ValueError(
                'Subscription datetime (%s) is earlier than '
                'current portfolio datetime (%s). Cannot '
                'subscribe funds.' % (dt, self.current_dt)
            )
        self.current_dt = dt

        if amount < 0.0:
            raise ValueError(
                'Cannot credit negative amount: '
                '%s to the portfolio.' % amount
            )

        self.cash += amount

        self.history.append(
            PortfolioEvent.create_subscription(self.current_dt, amount, self.cash)
        )

        self.logger.info(
            '(%s) Funds subscribed to portfolio "%s" '
            '- Credit: %0.2f, Balance: %0.2f' % (
                self.current_dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                self.portfolio_id, round(amount, 2),
                round(self.cash, 2)
            )
        )

    def withdraw_funds(self, dt, amount):
        """
        Withdraw funds from the portfolio if there is enough
        cash to allow it.
        """
        # Check that amount is positive and that there is
        # enough in the portfolio to withdraw the funds
        if dt < self.current_dt:
            raise ValueError(
                'Withdrawal datetime (%s) is earlier than '
                'current portfolio datetime (%s). Cannot '
                'withdraw funds.' % (dt, self.current_dt)
            )
        self.current_dt = dt

        if amount < 0:
            raise ValueError(
                'Cannot debit negative amount: '
                '%0.2f from the portfolio.' % amount
            )

        if amount > self.cash:
            raise ValueError(
                'Not enough cash in the portfolio to '
                'withdraw. %s withdrawal request exceeds '
                'current portfolio cash balance of %s.' % (
                    amount, self.cash
                )
            )

        self.cash -= amount

        self.history.append(
            PortfolioEvent.create_withdrawal(self.current_dt, amount, self.cash)
        )

        self.logger.info(
            '(%s) Funds withdrawn from portfolio "%s" '
            '- Debit: %0.2f, Balance: %0.2f' % (
                self.current_dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                self.portfolio_id, round(amount, 2),
                round(self.cash, 2)
            )
        )

    def transact_asset(self, txn):
        """
        Adjusts positions to account for a transaction.
        """
        if txn.dt < self.current_dt:
            raise ValueError(
                'Transaction datetime (%s) is earlier than '
                'current portfolio datetime (%s). Cannot '
                'transact assets.' % (txn.dt, self.current_dt)
            )
        self.current_dt = txn.dt

        txn_share_cost = txn.price * txn.quantity
        txn_total_cost = txn_share_cost + txn.commission

        if txn_total_cost > self.cash:
            if settings.PRINT_EVENTS:
                print(
                    'WARNING: Not enough cash in the portfolio to '
                    'carry out transaction. Transaction cost of %s '
                    'exceeds remaining cash of %s. Transaction '
                    'will proceed with a negative cash balance.' % (
                        txn_total_cost, self.cash
                    )
                )

        self.pos_handler.transact_position(txn)

        self.cash -= txn_total_cost

        # Form Portfolio history details
        direction = "LONG" if txn.direction > 0 else "SHORT"
        description = "%s %s %s %0.2f %s" % (
            direction, txn.quantity, txn.asset.upper(),
            txn.price, datetime.datetime.strftime(txn.dt, "%d/%m/%Y")
        )
        if direction == "LONG":
            pe = PortfolioEvent(
                dt=txn.dt, type='asset_transaction',
                description=description,
                debit=round(txn_total_cost, 2), credit=0.0,
                balance=round(self.cash, 2)
            )
            self.logger.info(
                '(%s) Asset "%s" transacted LONG in portfolio "%s" '
                '- Debit: %0.2f, Balance: %0.2f' % (
                    txn.dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                    txn.asset, self.portfolio_id,
                    round(txn_total_cost, 2), round(self.cash, 2)
                )
            )
        else:
            pe = PortfolioEvent(
                dt=txn.dt, type='asset_transaction',
                description=description,
                debit=0.0, credit=-1.0 * round(txn_total_cost, 2),
                balance=round(self.cash, 2)
            )
            self.logger.info(
                '(%s) Asset "%s" transacted SHORT in portfolio "%s" '
                '- Credit: %0.2f, Balance: %0.2f' % (
                    txn.dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                    txn.asset, self.portfolio_id,
                    -1.0 * round(txn_total_cost, 2), round(self.cash, 2)
                )
            )
        self.history.append(pe)

    def portfolio_to_dict(self):
        """
        Output the portfolio holdings information as a dictionary
        with Assets as keys and sub-dictionaries as values.
        This excludes cash.

        Returns
        -------
        `dict`
            The portfolio holdings.
        """
        holdings = {}
        for asset, pos in self.pos_handler.positions.items():
            holdings[asset] = {
                "quantity": pos.net_quantity,
                "market_value": pos.market_value,
                "unrealised_pnl": pos.unrealised_pnl,
                "realised_pnl": pos.realised_pnl,
                "total_pnl": pos.total_pnl
            }
        return holdings

    def update_market_value_of_asset(
        self, asset, current_price, current_dt
    ):
        """
        Update the market value of the asset to the current
        trade price and date.
        """
        if asset not in self.pos_handler.positions:
            return
        else:
            if current_price < 0.0:
                raise ValueError(
                    'Current trade price of %s is negative for '
                    'asset %s. Cannot update position.' % (
                        current_price, asset
                    )
                )

            if current_dt < self.current_dt:
                raise ValueError(
                    'Current trade date of %s is earlier than '
                    'current date %s of asset %s. Cannot update '
                    'position.' % (
                        current_dt, self.current_dt, asset
                    )
                )

            self.pos_handler.positions[asset].update_current_price(
                current_price, current_dt
            )

    def history_to_df(self):
        """
        Creates a Pandas DataFrame of the Portfolio history.
        """
        records = [pe.to_dict() for pe in self.history]
        return pd.DataFrame.from_records(
            records, columns=[
                "date", "type", "description", "debit", "credit", "balance"
            ]
        ).set_index(keys=["date"])
