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

from qstrader.broker.position import Position
from qstrader.broker.transaction import Transaction


class EquityMock(object):
    """Mock object for the Asset-derived Equity class."""

    def __init__(self, asset_id, exchange=None):
        self.__name__ = "Equity"
        self.asset_id = asset_id
        self.exchange = exchange

    def __str__(self):
        return "%s(%s)" % (self.__name__, self.asset_id)


class PositionTests(unittest.TestCase):
    """Tests that the Position class correctly assigns
    its attributes, that the object representation
    correctly recreates the object and that the 'update'
    method correctly calculates quantities and cost bases
    for various transaction scenarios.
    """

    def test_position_representation(self):
        """
        Tests that the Position representation
        correctly recreates the object.
        """
        asset = EquityMock(1, exchange='NYSE')
        position = Position(
            asset, quantity=153, book_cost_ps=950.0,
            current_trade_price=950.0
        )
        exp_repr = (
            "Position(asset=Equity(1), quantity=153, "
            "book_cost_ps=950.0, current_trade_price=950.0)"
        )
        self.assertEqual(repr(position), exp_repr)

    def test_position_long_twice(self):
        """
        Tests that the quantity and book cost are
        correctly calculated for an initial long
        position with an additional long transaction
        in the same asset.
        """
        asset = EquityMock(1, exchange='NYSE')
        position = Position(
            asset, quantity=100, book_cost_ps=950.0,
            current_trade_price=950.0
        )
        dt = pd.Timestamp('2015-05-06')
        transaction = Transaction(
            asset, quantity=100, dt=dt, price=960.0,
            order_id=123, commission=None
        )
        position.update(transaction)
        self.assertEqual(position.quantity, 200)
        self.assertEqual(position.book_cost_ps, 955.0)
        self.assertEqual(position.direction, 1.0)
        self.assertEqual(position.current_trade_price, 960.0)

    def test_position_long_close(self):
        """
        Tests that the quantity and book cost are
        correctly calculated for an initial long
        position with an additional short transaction
        in the same asset, where the short closes
        the position.
        """
        asset = EquityMock(1, exchange='NYSE')
        position = Position(
            asset, quantity=100, book_cost_ps=950.0,
            current_trade_price=950.0
        )
        dt = pd.Timestamp('2015-05-06')
        transaction = Transaction(
            asset, quantity=-100, dt=dt, price=960.0,
            order_id=123, commission=None
        )
        position.update(transaction)
        self.assertEqual(position.quantity, 0)
        self.assertEqual(position.book_cost_ps, 0.0)
        self.assertEqual(position.direction, 1.0)
        self.assertEqual(position.current_trade_price, 960.0)

    def test_position_long_short(self):
        """
        Tests that the quantity and book cost are
        correctly calculated for an initial long
        position with an additional short transaction
        in the same asset, where the short does not
        completely eliminate the position.
        """
        asset = EquityMock(1, exchange='NYSE')
        position = Position(
            asset, quantity=100, book_cost_ps=950.0,
            current_trade_price=950.0
        )
        dt = pd.Timestamp('2015-05-06')
        transaction = Transaction(
            asset, quantity=-50, dt=dt, price=960.0,
            order_id=123, commission=None
        )
        position.update(transaction)
        self.assertEqual(position.quantity, 50)
        self.assertEqual(position.book_cost_ps, 950.0)
        self.assertEqual(position.direction, 1.0)
        self.assertEqual(position.current_trade_price, 960.0)

    def test_position_short_twice(self):
        """
        Tests that the quantity and book cost are
        correctly calculated for an initial short
        position with an additional short transaction
        in the same asset.
        """
        asset = EquityMock(1, exchange='NYSE')
        position = Position(
            asset, quantity=-100, book_cost_ps=950.0,
            current_trade_price=950.0
        )
        dt = pd.Timestamp('2015-05-06')
        transaction = Transaction(
            asset, quantity=-100, dt=dt, price=960.0,
            order_id=123, commission=None
        )
        position.update(transaction)
        self.assertEqual(position.quantity, -200)
        self.assertEqual(position.book_cost_ps, 955.0)
        self.assertEqual(position.direction, -1.0)
        self.assertEqual(position.current_trade_price, 960.0)

    def test_position_short_close(self):
        """
        Tests that the quantity and book cost are
        correctly calculated for an initial short
        position with an additional long transaction
        in the same asset, where the long closes
        the position.
        """
        asset = EquityMock(1, exchange='NYSE')
        position = Position(
            asset, quantity=-100, book_cost_ps=950.0,
            current_trade_price=950.0
        )
        dt = pd.Timestamp('2015-05-06')
        transaction = Transaction(
            asset, quantity=100, dt=dt, price=960.0,
            order_id=123, commission=None
        )
        position.update(transaction)
        self.assertEqual(position.quantity, 0)
        self.assertEqual(position.book_cost_ps, 0.0)
        self.assertEqual(position.direction, 1.0)
        self.assertEqual(position.current_trade_price, 960.0)

    def test_position_short_long(self):
        """
        Tests that the quantity and book cost are
        correctly calculated for an initial short
        position with an additional long transaction
        in the same asset, where the long does not
        completely eliminate the position.
        """
        asset = EquityMock(1, exchange='NYSE')
        position = Position(
            asset, quantity=-100, book_cost_ps=950.0,
            current_trade_price=950.0
        )
        dt = pd.Timestamp('2015-05-06')
        transaction = Transaction(
            asset, quantity=50, dt=dt, price=960.0,
            order_id=123, commission=None
        )
        position.update(transaction)
        self.assertEqual(position.quantity, -50)
        self.assertEqual(position.book_cost_ps, 950.0)
        self.assertEqual(position.direction, -1.0)
        self.assertEqual(position.current_trade_price, 960.0)

    def test_update_for_incorrect_asset(self):
        """
        Tests that the 'update' method, when provided
        with a transaction with an asset that does not
        match the position's asset, raises an Exception.
        """
        asset1 = EquityMock(1, exchange='NYSE')
        asset2 = EquityMock(2, exchange='NYSE')
        position = Position(
            asset1, quantity=100, book_cost_ps=950.0,
            current_trade_price=950.0
        )
        dt = pd.Timestamp('2015-05-06')
        transaction = Transaction(
            asset2, quantity=50, dt=dt, price=960.0,
            order_id=123, commission=None
        )
        with self.assertRaises(Exception):
            position.update(transaction)

    def test_update_book_cost_for_commission_for_incorrect_asset(self):
        """
        Tests that the 'update_book_cost_for_commission'
        method, when provided with a transaction with an
        asset that does not match the position's asset,
        raises an Exception.
        """
        asset1 = EquityMock(1, exchange='NYSE')
        asset2 = EquityMock(2, exchange='NYSE')
        position = Position(
            asset1, quantity=100, book_cost_ps=950.0,
            current_trade_price=950.0
        )
        with self.assertRaises(Exception):
            position.update_book_cost_for_commission(asset2, 23.00)

    def test_update_book_cost_for_commission_for_no_commission(self):
        """
        Tests that 'update_book_cost_for_commission' returns None
        when zero or None commission is provided.
        """
        asset = EquityMock(1, exchange='NYSE')
        position = Position(
            asset, quantity=100, book_cost_ps=950.0,
            current_trade_price=950.0
        )
        self.assertEqual(
            position.update_book_cost_for_commission(asset, 0.0),
            None
        )
        self.assertEqual(
            position.update_book_cost_for_commission(asset, None),
            None
        )


if __name__ == "__main__":
    unittest.main()
