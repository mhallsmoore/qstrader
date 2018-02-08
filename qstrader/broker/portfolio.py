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

import datetime
from collections import namedtuple
import locale
import logging
import math
import sys

import pandas as pd

from qstrader.broker.position_handler import PositionHandler
from qstrader import settings
from qstrader.utils.console import (
    string_colour, GREEN, RED, CYAN, WHITE
)


PortfolioEvent = namedtuple(
    'PortfolioEvent', 'date, type, description, debit, credit, balance'
)


class PortfolioException(Exception):
    pass


class Portfolio(object):
    """A class representing a portfolio. It contains a cash
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
        self, start_dt, starting_cash=0.0,
        currency="USD", portfolio_id=None,
        name=None
    ):
        """
        Initialise the Portfolio object with a PositionHandler,
        an event history, along with cash balance. Make sure
        the portfolio denomination currency is also set.
        """
        self.pos_handler = PositionHandler()
        self.history = []
        self.start_dt = start_dt
        self.cur_dt = start_dt
        self.currency = currency
        self._set_currency()
        self.starting_cash = starting_cash
        self.portfolio_id = portfolio_id
        self.name = name
        self.total_value = starting_cash
        self.total_cash = starting_cash
        self.total_equity = starting_cash

        self.logger = logging.getLogger('Portfolio')
        self.logger.setLevel(logging.DEBUG)
        self.logger.info(
            '(%s) Portfolio "%s" instance initialised' % (
                self.cur_dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                self.portfolio_id
            )
        )

    def _set_currency(self):
        """
        Apply the correct currency symbols. Currently
        supports USD and GBP.
        """
        if self.currency == "GBP":
            locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')
        elif self.currency == "USD":
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        else:
            raise PortfolioException(
                'Currency of "%s" not currently supported yet. '
                'Please create a Portfolio with GBP or USD as '
                'currency.' % self.currency
            )

    def _currency_format(self, amount):
        """
        Format the amount in correct format for a paticular
        currency. Currently supports USD and GBP.
        """
        return locale.currency(amount, grouping=True)

    def subscribe_funds(self, dt, amount):
        """
        Credit funds to the portfolio.
        """
        if dt < self.cur_dt:
            raise PortfolioException(
                'Subscription datetime (%s) is earlier than '
                'current portfolio datetime (%s). Cannot '
                'subscribe funds.' % (dt, self.cur_dt)
            )
        if amount < 0:
            raise PortfolioException(
                'Cannot credit negative amount: '
                '%s to the portfolio.' %
                self._currency_format(amount)
            )
        self.total_cash += amount
        self.total_value += amount
        self.total_equity += amount
        pe = PortfolioEvent(
            date=dt, type='subscription',
            description="SUBSCRIPTION",
            debit=0.0, credit=round(amount, 2),
            balance=round(self.total_cash, 2)
        )
        self.history.append(pe)
        self.cur_dt = dt
        self.logger.info(
            '(%s) Funds subscribed to portfolio "%s" '
            '- Credit: %0.2f, Balance: %0.2f' % (
                self.cur_dt.strftime(settings.LOGGING["DATE_FORMAT"]),
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
        if dt < self.cur_dt:
            raise PortfolioException(
                'Withdrawal datetime (%s) is earlier than '
                'current portfolio datetime (%s). Cannot '
                'withdraw funds.' % (dt, self.cur_dt)
            )
        if amount < 0:
            raise PortfolioException(
                'Cannot debit negative amount: '
                '%0.2f from the portfolio.' % amount
            )
        if amount > self.total_cash:
            raise PortfolioException(
                'Not enough cash in the portfolio to '
                'withdraw. %s withdrawal request exceeds '
                'current portfolio cash balance of %s.' % (
                    self._currency_format(amount),
                    self._currency_format(self.total_cash)
                )
            )
        self.total_cash -= amount
        self.total_value -= amount
        self.total_equity -= amount
        pe = PortfolioEvent(
            date=dt, type='withdrawal',
            description="WITHDRAWAL",
            debit=round(amount, 2), credit=0.0,
            balance=round(self.total_cash, 2)
        )
        self.history.append(pe)
        self.cur_dt = dt
        self.logger.info(
            '(%s) Funds withdrawn from portfolio "%s" '
            '- Debit: %0.2f, Balance: %0.2f' % (
                self.cur_dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                self.portfolio_id, round(amount, 2),
                round(self.total_cash, 2)
            )
        )

    def transact_asset(self, transaction):
        """
        Adjusts positions to account for a transaction.
        """
        tn = transaction
        if tn.dt < self.cur_dt:
            raise PortfolioException(
                'Transaction datetime (%s) is earlier than '
                'current portfolio datetime (%s). Cannot '
                'transact assets.' % (tn.dt, self.cur_dt)
            )
        tn_share_cost = tn.price * tn.quantity
        tn_total_cost = tn_share_cost + tn.commission

        if tn_total_cost > self.total_cash:
            raise PortfolioException(
                'Not enough cash in the portfolio to '
                'carry out transaction. Transaction cost of %s '
                'exceeds remaining cash of %s.' % (
                    self._currency_format(tn_total_cost),
                    self._currency_format(self.total_cash)
                )
            )
        self.pos_handler.transact_position(tn)
        self.total_cash -= tn_total_cost
        self.total_value -= tn.commission
        self.total_equity -= tn.commission

        # Form Portfolio history details
        direction = "LONG" if tn.direction > 0 else "SHORT"
        description = "%s %s %s %0.2f %s" % (
            direction, tn.quantity, tn.asset.name.upper(),
            tn.price, datetime.datetime.strftime(tn.dt, "%d/%m/%Y")
        )
        if direction == "LONG":
            pe = PortfolioEvent(
                date=tn.dt, type='asset_transaction',
                description=description,
                debit=round(tn_total_cost, 2), credit=0.0,
                balance=round(self.total_cash, 2)
            )
            self.logger.info(
                '(%s) Asset "%s" transacted LONG in portfolio "%s" '
                '- Debit: %0.2f, Balance: %0.2f' % (
                    tn.dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                    tn.asset.symbol, self.portfolio_id,
                    round(tn_total_cost, 2), round(self.total_cash, 2)
                )
            )
        else:
            pe = PortfolioEvent(
                date=tn.dt, type='asset_transaction',
                description=description,
                debit=0.0, credit=-1.0*round(tn_total_cost, 2),
                balance=round(self.total_cash, 2)
            )
            self.logger.info(
                '(%s) Asset "%s" transacted SHORT in portfolio "%s" '
                '- Credit: %0.2f, Balance: %0.2f' % (
                    tn.dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                    tn.asset.symbol, self.portfolio_id,
                    -1.0*round(tn_total_cost, 2), round(self.total_cash, 2)
                )
            )
        self.history.append(pe)
        self.cur_dt = transaction.dt

    def cash_dividend(self, dt, asset, div_per_share):
        """
        This causes the portfolio to receive a cash
        dividend on a particular asset.
        """
        if dt < self.cur_dt:
            raise PortfolioException(
                'Dividend datetime (%s) is earlier than '
                'current portfolio datetime (%s). Cannot '
                'create dividend.' % (dt, self.cur_dt)
            )
        if asset not in self.pos_handler.positions:
            raise PortfolioException(
                'Asset %s not in portfolio so cannot '
                'receive a dividend per share of %s.' % (
                    asset.name, self._currency_format(div_per_share)
                )
            )
        if div_per_share < 0.0:
            raise PortfolioException(
                'Dividend per share of %s is negative for '
                'asset %s. Cannot create dividend.' % (
                    self._currency_format(div_per_share), asset.name
                )
            )
        quantity = self.pos_handler.positions[asset].quantity

        # Some brokerages use the following rounding
        # methodology # on their dividends:
        total_div = math.floor(
            (div_per_share * quantity) * 100.0
        ) / 100.0

        self.total_cash += total_div
        self.total_value += total_div
        self.total_equity += total_div
        description = "DIVIDEND %s %s %0.2f%s %s" % (
            quantity, asset.name.upper(),
            div_per_share, self.currency,
            datetime.datetime.strftime(dt, "%d/%m/%Y")
        )
        pe = PortfolioEvent(
            date=dt, type='dividend',
            description=description,
            debit=0.0, credit=total_div,
            balance=round(self.total_cash, 2)
        )
        self.history.append(pe)
        self.cur_dt = dt
        self.logger.info(
            '(%s) %0.2f subscribed to broker account "%s"' % (
                self.cur_dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                amount, self.account_id
            )
        )

    def update_market_value_of_asset(
        self, asset, current_trade_price, current_trade_date
    ):
        """
        Update the market value of the asset to the current
        trade price and date.
        """
        if asset not in self.pos_handler.positions:
            return
        else:
            if current_trade_price < 0.0:
                raise PortfolioException(
                    'Current trade price of %s is negative for '
                    'asset %s. Cannot update position.' % (
                        current_trade_price, asset
                    )
                )
            if current_trade_date < self.cur_dt:
                raise PortfolioException(
                    'Current trade date of %s is earlier than '
                    'current date %s of asset %s. Cannot update '
                    'position.' % (
                        current_trade_date, self.cur_dt, asset
                    )
                )
            self.pos_handler.update_position(
                asset,
                current_trade_price=current_trade_price,
                current_trade_date=current_trade_date
            )

    def history_to_df(self):
        """
        Creates a Pandas DataFrame of the Portfolio history.
        """
        df = pd.DataFrame.from_records(
            self.history, columns=[
                "date", "type", "description",
                "debit", "credit", "balance"
            ]
        )
        df.set_index(keys=["date"], inplace=True)
        return df

    def holdings_to_dict(self):
        """
        Output the portfolio holdings information as a dictionary
        with Assets as keys and sub-dictionaries as values.
        """
        holdings = {}
        for asset, pos in self.pos_handler.positions.items():
            holdings[asset] = {
                "quantity": pos.quantity,
                "book_cost": pos.book_cost,
                "market_value": pos.market_value,
                "gain": pos.unr_gain,
                "perc_gain": pos.unr_perc_gain
            }
        return holdings

    def portfolio_to_dict(self):
        """
        Output the portfolio holdings information as a dictionary
        with Assets as keys and sub-dictionaries as values, with
        the inclusion of total cash and total value.
        """
        port_dict = self.holdings_to_dict()
        port_dict["total_cash"] = self.total_cash
        port_dict["total_value"] = self.total_value
        port_dict["total_equity"] = self.total_equity
        return port_dict

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
            key=lambda x: x[0].name
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
        repeats = 98
        print_row_divider(repeats)
        sys.stdout.write(
            "| Holding | Quantity | Price | Change |"
            "      Book Cost |   Market Value |       "
            "     Gain          | \n"
        )
        print_row_divider(repeats)

        # Create the asset holdings rows for each ticker
        ticker_format = '| {0:>7} | {1:>8d} | {2:>5} | ' \
            '{3:>6} | {4:>14} | {5:>14} |'
        for asset, pos in pos_sorted:
            sys.stdout.write(
                ticker_format.format(
                    asset.symbol, int(pos.quantity), "-", "-",
                    self._currency_format(pos.book_cost),
                    self._currency_format(pos.market_value)
                )
            )
            # Colour the gain as red, green or white depending upon
            # whether it is negative, positive or breakeven
            colour = WHITE
            if pos.unr_gain > 0.0:
                colour = GREEN
            elif pos.unr_gain < 0.0:
                colour = RED
            gain_str = string_colour(
                self._currency_format(
                    pos.unr_gain
                ), colour=colour
            )
            perc_gain_str = string_colour(
                "%0.2f%%" % pos.unr_perc_gain,
                colour=colour
            )
            sys.stdout.write(" " * (25 - len(gain_str)))
            sys.stdout.write(gain_str)
            sys.stdout.write(" " * (22 - len(perc_gain_str)))
            sys.stdout.write(str(perc_gain_str))
            sys.stdout.write(" |\n")

        # Create the totals row
        print_row_divider(repeats)
        total_format = '| {0:>7} | {1:25} | {2:>14} | {3:>14} |'
        sys.stdout.write(
            total_format.format(
                "Total", " ",
                self._currency_format(self.pos_handler.total_book_cost()),
                self._currency_format(self.pos_handler.total_market_value())
            )
        )
        # Utilise the correct colour for the totals
        # of gain and percentage gain
        colour = WHITE
        total_gain = self.pos_handler.total_unr_gain()
        perc_total_gain = self.pos_handler.total_unr_perc_gain()
        if total_gain > 0.0:
            colour = GREEN
        elif total_gain < 0.0:
            colour = RED
        gain_str = string_colour(
            self._currency_format(total_gain),
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

    def update(self, dt):
        """
        TODO: Fill in this doc string!
        """
        self.total_value = 0.0
        self.total_value = self.pos_handler.total_market_value()
        self.total_value += self.total_cash

        self.total_equity = 0.0
        self.total_equity = self.pos_handler.total_unr_gain()
        self.total_equity += self.total_cash
