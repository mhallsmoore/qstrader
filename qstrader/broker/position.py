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

import numpy as np


class PositionException(object):
    pass


class Position(object):
    """A class that keeps track of the position in an asset
    as registered at a particular Broker, in a Portfolio.

    Includes the whole number of shares, the current trade
    price and the position book cost (VWAP per share).

    Parameters
    ----------
    asset : Asset
        The asset of the position
    quantity : int, optional
        Whole number quantity of shares in the position
    book_cost_ps : float, optional
        Volume weighted average price per share of
        the position (the book cost per share)
    current_trade_price : float, optional
        The most recently known trade price of the asset
        on the exchange, as known to the Position
    current_trade_date : datetime, optional
        The most recently known trade date of the asset
        on the exchange, as known to the Position
    """

    def __init__(
        self, asset, quantity=0, book_cost_ps=0.0,
        current_trade_price=0.0, current_trade_date=None
    ):
        """
        Initialise the Position object and calculate the
        position direction (long or short), represented
        by a +1 or -1.
        """
        self.asset = asset
        self.quantity = quantity
        self.direction = np.copysign(1, self.quantity)
        self.book_cost_ps = book_cost_ps
        self.current_trade_price = current_trade_price
        self.current_trade_date = current_trade_date
        self.book_cost = self.book_cost_ps * self.quantity

    def __repr__(self):
        """
        Provides a representation of the Position object to allow
        full recreation of the object.
        """
        return "%s(asset=%s, quantity=%s, book_cost_ps=%s, " \
            "current_trade_price=%s)" % (
                self.__class__.__name__, self.asset, self.quantity,
                self.book_cost_ps, self.current_trade_price
            )

    def update_book_cost_for_commission(self, asset, commission):
        """
        Handles the adjustment to the position book cost due to
        trading commissions.
        """
        if self.asset != asset:
            raise PositionException(
                'Failed to adjust book cost for Position on asset '
                '%s due to attempt being made to adjust asset %s.' % {
                    self.asset, asset
                }
            )

        # If there's no commission, then there's nothing to do
        if commission is None or commission == 0.0:
            return None

        # If the quantity is zero (position is no longer held)
        # then the book cost is also zero, so does not need adjusting
        if self.quantity == 0:
            return None

        # For simplicity the commission costs are 'shared'
        # across all shares in a position
        position_cost = self.book_cost_ps * self.quantity
        final_cost = position_cost + commission
        self.book_cost_ps = final_cost / self.quantity
        self.book_cost = self.book_cost_ps * self.quantity

    def update(self, transaction):
        """
        Calculates the adjustments to the Position that occur
        once new shares in an asset are bought and sold.
        """
        if self.asset != transaction.asset:
            raise PositionException(
                'Failed to update Position with asset %s when '
                'carrying out transaction of shares in asset %s. ' % (
                    self.asset, transaction.asset
                )
            )

        # Sum the position and transaction quantities then
        # adjust book cost depending upon transaction direction
        total_quantity = self.quantity + transaction.quantity
        if total_quantity == 0:
            self.book_cost_ps = 0.0
            self.book_cost = 0.0
        else:
            if self.direction == transaction.direction:
                # Increasing a long or short position
                position_cost = self.book_cost_ps * self.quantity
                transaction_cost = transaction.quantity * transaction.price
                total_cost = position_cost + transaction_cost
                self.book_cost_ps = total_cost / total_quantity
            else:
                # Closing a position out or covering a short position
                if abs(transaction.quantity) > abs(self.quantity):
                    # Transaction quantity exceeds position quantity
                    # so a long position is closed and short position
                    # is open, or a short position has been covered
                    # and we've now gone long
                    self.book_cost_ps = transaction.price

        # Update the current trade information
        if (
            self.current_trade_date is None or
            transaction.dt > self.current_trade_date
        ):
            self.current_trade_price = transaction.price
            self.current_trade_date = transaction.dt

        # Update to the new quantity of shares
        self.quantity = total_quantity

        # Handle the commission cost to adjust book cost
        # per share and total book cost
        self.update_book_cost_for_commission(
            self.asset, transaction.commission
        )

        # Adjust the total book cost and position direction
        self.book_cost = self.book_cost_ps * self.quantity
        self.direction = np.copysign(1, self.quantity)

    @property
    def market_value(self):
        """
        Return the market value of the position based on the
        current trade price provided.
        """
        return self.current_trade_price * self.quantity

    @property
    def gain(self):
        """
        Calculate the absolute gain in currency of the position
        based solely on the market value (i.e. remaining
        unrealised gains).
        """
        return self.market_value - self.book_cost

    @property
    def perc_gain(self):
        """
        Calculate the percentage gain of the position based solely
        on the market value (i.e. remaining unrealised percentage
        gains).
        """
        return (self.gain/self.book_cost)*100.0
