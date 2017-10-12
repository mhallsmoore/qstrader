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

from collections import OrderedDict
import inspect

from qstrader.broker.position import Position


class PositionHandler(object):
    """A class that keeps track of, and updates, the current
    list of Position instances stored in a Portfolio entity.
    """

    def __init__(self):
        """
        Initialise the PositionHandler object to generate
        an ordered dictionary containing the current positions.
        """
        self.positions = OrderedDict()

    def _check_set_position(self, asset):
        """
        Checks if a position exists in the positions list
        and if not creates a new key, and Position instance
        for this particular asset.
        """
        if asset in self.positions:
            position = self.positions[asset]
        else:
            position = Position(asset)
            self.positions[asset] = position
        return position

    def transact_position(self, transaction):
        """
        Execute the transaction and update the appropriate
        position for the transaction's asset accordingly.
        """
        position = self._check_set_position(transaction.asset)
        position.update(transaction)

        # If the position has zero quantity remove it
        if position.quantity == 0:
            del self.positions[transaction.asset]

    def update_position(
        self, asset, quantity=None, current_trade_price=None,
        current_trade_date=None, book_cost_ps=None
    ):
        """
        Update the attributes of a particular Position
        via its Asset.
        """
        position = self._check_set_position(asset)

        # Update each position attribute if
        # the parameters aren't None
        frame = inspect.currentframe()
        varvals = inspect.getargvalues(frame)
        for attr in (
            'quantity', 'current_trade_price',
            'current_trade_date', 'book_cost_ps'
        ):
            if varvals.locals[attr] is not None:
                setattr(position, attr, varvals.locals[attr])

    def update_commission(self, asset, commission):
        """
        Adjust the book cost per share of the position
        instance for this particular asset.
        """
        if asset in self.positions:
            self.positions[asset].update_book_cost_for_commission(
                asset, commission
            )

    def total_book_cost(self):
        """
        Calculate the sum of all the positions' book costs.
        """
        return sum(
            pos.book_cost 
            for asset, pos in self.positions.items()
        )

    def total_market_value(self):
        """
        Calculate the sum of all the positions' market values.
        """
        return sum(
            pos.market_value
            for asset, pos in self.positions.items()
        )

    def total_unr_gain(self):
        """
        Calculate the sum of all the positions'
        unrealised gains.
        """
        return sum(
            pos.unr_gain
            for asset, pos in self.positions.items()
        )

    def total_unr_perc_gain(self):
        """
        Calculate the total unrealised percentage gain
        on the positions.
        """
        tbc = self.total_book_cost()
        if tbc == 0.0:
            return 0.0
        return (self.total_market_value() - tbc)/tbc*100.0
