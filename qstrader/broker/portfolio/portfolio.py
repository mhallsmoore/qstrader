import datetime
import logging
import sys

import pandas as pd

from qstrader import settings
from qstrader.asset.asset import Asset
from qstrader.broker.portfolio.portfolio_event import PortfolioEvent
from qstrader.broker.portfolio.position import Position
from qstrader.broker.portfolio.position_handler import PositionHandler
from qstrader.utils.console import (
    string_colour, GREEN, RED, CYAN, WHITE
)


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
        cash_position = Position(
            self.cash_position_key,
            self.starting_cash,
            book_cost_pu=1.0,
            current_price=1.0,
            current_dt=self.current_dt
        )
        self.pos_handler.positions[self.cash_position_key] = cash_position

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
    def cash_position_key(self):
        """
        Obtain the PositionHandler dictionary key for the default
        currency Cash Asset Position.
        """
        return 'CASH:%s' % self.currency

    @property
    def total_cash(self):
        """
        Obtain the total cash available in the default currency
        within the Portfolio.
        """
        cash_position = self.pos_handler.positions[self.cash_position_key]
        return cash_position.quantity

    @property
    def total_equity(self):
        """
        Obtain the total market value of the portfolio including cash.
        """
        return self.pos_handler.total_market_value()

    @property
    def total_non_cash_equity(self):
        """
        Obtain the total market value of the portfolio excluding cash.
        """
        return self.total_equity - self.total_cash

    @property
    def total_non_cash_unrealised_gain(self):
        """
        Calculate the sum of all the positions'
        unrealised gains.
        """
        return sum(
            pos.unrealised_gain
            for asset, pos in self.pos_handler.positions.items()
            if not asset.startswith('CASH')
        )

    @property
    def total_non_cash_unrealised_percentage_gain(self):
        """
        Calculate the total unrealised percentage gain
        on the positions.
        """
        tbc = self.pos_handler.total_book_cost()
        if tbc == 0.0:
            return 0.0
        return (self.total_non_cash_equity - tbc) / tbc * 100.0

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

        cash_position = self.pos_handler.positions[self.cash_position_key]

        new_quantity = cash_position.quantity + amount
        self.pos_handler.update_position(
            self.cash_position_key,
            quantity=new_quantity,
            current_dt=self.current_dt
        )

        self.history.append(
            PortfolioEvent.create_subscription(self.current_dt, amount, self.total_cash)
        )

        self.logger.info(
            '(%s) Funds subscribed to portfolio "%s" '
            '- Credit: %0.2f, Balance: %0.2f' % (
                self.current_dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                self.portfolio_id, round(amount, 2),
                round(self.total_cash, 2)
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

        if amount > self.total_cash:
            raise ValueError(
                'Not enough cash in the portfolio to '
                'withdraw. %s withdrawal request exceeds '
                'current portfolio cash balance of %s.' % (
                    amount, self.total_cash
                )
            )

        cash_position = self.pos_handler.positions[self.cash_position_key]

        new_quantity = cash_position.quantity - amount
        self.pos_handler.update_position(
            self.cash_position_key,
            quantity=new_quantity,
            current_dt=self.current_dt
        )

        self.history.append(
            PortfolioEvent.create_withdrawal(self.current_dt, amount, self.total_cash)
        )

        self.logger.info(
            '(%s) Funds withdrawn from portfolio "%s" '
            '- Debit: %0.2f, Balance: %0.2f' % (
                self.current_dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                self.portfolio_id, round(amount, 2),
                round(self.total_cash, 2)
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

        if txn_total_cost > self.total_cash:
            raise ValueError(
                'Not enough cash in the portfolio to '
                'carry out transaction. Transaction cost of %s '
                'exceeds remaining cash of %s.' % (
                    txn_total_cost, self.total_cash
                )
            )

        self.pos_handler.transact_position(txn)
        cash_position = self.pos_handler.positions[self.cash_position_key]

        new_cash_quantity = cash_position.quantity - txn_total_cost
        self.pos_handler.update_position(
            self.cash_position_key,
            quantity=new_cash_quantity,
            current_dt=self.current_dt
        )

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
                balance=round(self.total_cash, 2)
            )
            self.logger.info(
                '(%s) Asset "%s" transacted LONG in portfolio "%s" '
                '- Debit: %0.2f, Balance: %0.2f' % (
                    txn.dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                    txn.asset, self.portfolio_id,
                    round(txn_total_cost, 2), round(self.total_cash, 2)
                )
            )
        else:
            pe = PortfolioEvent(
                dt=txn.dt, type='asset_transaction',
                description=description,
                debit=0.0, credit=-1.0 * round(txn_total_cost, 2),
                balance=round(self.total_cash, 2)
            )
            self.logger.info(
                '(%s) Asset "%s" transacted SHORT in portfolio "%s" '
                '- Credit: %0.2f, Balance: %0.2f' % (
                    txn.dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                    txn.asset, self.portfolio_id,
                    -1.0 * round(txn_total_cost, 2), round(self.total_cash, 2)
                )
            )
        self.history.append(pe)

    def portfolio_to_dict(self):
        """
        Output the portfolio holdings information as a dictionary
        with Assets as keys and sub-dictionaries as values.

        This excludes Cash assets.
        """
        holdings = {}
        for asset, pos in self.pos_handler.positions.items():
            if not issubclass(asset.__class__, Asset) and not asset.startswith('CASH'):
                holdings[asset] = {
                    "quantity": pos.quantity,
                    "book_cost": pos.book_cost,
                    "market_value": pos.market_value,
                    "gain": pos.unrealised_gain,
                    "perc_gain": pos.unrealised_percentage_gain
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

            self.pos_handler.update_position(
                asset,
                current_price=current_price,
                current_dt=current_dt
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

    def holdings_to_console(self):
        """
        Output the portfolio holdings information to the console.
        """
        def print_row_divider(repeats, symbol="=", cap="*"):
            """
            Prints a row divider for the table.
            """
            sys.stdout.write(
                "%s%s%s\n" % (cap, symbol * repeats, cap)
            )

        # Sort the assets based on their name, not ticker symbol
        pos_sorted = sorted(
            self.pos_handler.positions.items(),
            key=lambda x: x[0]
        )

        # Output the name and ID of the portfolio
        sys.stdout.write(
            string_colour(
                "\nPortfolio Holdings | %s - %s\n\n" % (
                    self.portfolio_id, self.name
                ), colour=CYAN
            )
        )

        # Create the header row and dividers
        repeats = 99
        print_row_divider(repeats)
        sys.stdout.write(
            "|  Holding | Quantity | Price | Change |"
            "      Book Cost |   Market Value |     "
            " Unrealised Gain     | \n"
        )
        print_row_divider(repeats)

        # Create the asset holdings rows for each ticker
        ticker_format = '| {0:>8} | {1:>8d} | {2:>5} | ' \
            '{3:>6} | {4:>14} | {5:>14} |'
        for asset, pos in pos_sorted:
            if asset.startswith('CASH'):
                pos_quantity = 0
                pos_book_cost = pos.market_value
                pos_unrealised_gain = '0.00'
                pos_unrealised_percentage_gain = '0.00%'
            else:
                pos_quantity = int(pos.quantity)
                pos_book_cost = pos.book_cost
                pos_unrealised_gain = "%0.2f" % pos.unrealised_gain
                pos_unrealised_percentage_gain = "%0.2f%%" % pos.unrealised_percentage_gain
            sys.stdout.write(
                ticker_format.format(
                    asset, pos_quantity, "-", "-",
                    "%0.2f" % pos_book_cost,
                    "%0.2f" % pos.market_value
                )
            )
            # Colour the gain as red, green or white depending upon
            # whether it is negative, positive or breakeven
            colour = WHITE
            if pos.unrealised_gain > 0.0:
                colour = GREEN
            elif pos.unrealised_gain < 0.0:
                colour = RED
            gain_str = string_colour(
                pos_unrealised_gain,
                colour=colour
            )
            perc_gain_str = string_colour(
                pos_unrealised_percentage_gain,
                colour=colour
            )
            sys.stdout.write(" " * (25 - len(gain_str)))
            sys.stdout.write(gain_str)
            sys.stdout.write(" " * (22 - len(perc_gain_str)))
            sys.stdout.write(str(perc_gain_str))
            sys.stdout.write(" |\n")

        # Create the totals row
        print_row_divider(repeats)
        total_format = '| {0:>8} | {1:25} | {2:>14} | {3:>14} |'
        sys.stdout.write(
            total_format.format(
                "Total", " ",
                "%0.2f" % self.pos_handler.total_book_cost(),
                "%0.2f" % self.pos_handler.total_market_value()
            )
        )
        # Utilise the correct colour for the totals
        # of gain and percentage gain
        colour = WHITE
        total_gain = self.pos_handler.total_unrealised_gain()
        perc_total_gain = self.pos_handler.total_unrealised_percentage_gain()
        if total_gain > 0.0:
            colour = GREEN
        elif total_gain < 0.0:
            colour = RED
        gain_str = string_colour(
            "%0.2f" % total_gain,
            colour=colour
        )
        perc_gain_str = string_colour(
            "%0.2f%%" % perc_total_gain,
            colour=colour
        )
        sys.stdout.write(" " * (25 - len(gain_str)))
        sys.stdout.write(gain_str)
        sys.stdout.write(" " * (22 - len(perc_gain_str)))
        sys.stdout.write(str(perc_gain_str))
        sys.stdout.write(" |\n")
        print_row_divider(repeats)
        sys.stdout.write("\n")
