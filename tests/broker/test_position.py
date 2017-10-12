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
        self.assertEqual(position.market_value, 192000.0)
        self.assertEqual(position.unr_gain, 1000.0)
        self.assertEqual(position.unr_perc_gain, 0.5235602094240838)

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
        self.assertEqual(position.market_value, 0.0)
        self.assertEqual(position.unr_gain, 0.0)
        self.assertEqual(position.unr_perc_gain, 0.0)

    def test_position_long_short_positive_gain(self):
        """
        Tests that the quantity and book cost are
        correctly calculated for an initial long
        position with an additional short transaction
        in the same asset, where the short does not
        completely eliminate the position and the
        result is a gain.
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
        self.assertEqual(position.market_value, 48000.0)
        self.assertEqual(position.unr_gain, 500.0)
        self.assertEqual(position.unr_perc_gain, 1.0526315789473684)

    def test_position_long_short_negative_gain(self):
        """
        Tests that the quantity and book cost are
        correctly calculated for an initial long
        position with an additional short transaction
        in the same asset, where the short does not
        completely eliminate the position and the
        result is a loss.
        """
        asset = EquityMock(1, exchange='NYSE')
        position = Position(
            asset, quantity=100, book_cost_ps=960.0,
            current_trade_price=950.0
        )
        dt = pd.Timestamp('2015-05-06')
        transaction = Transaction(
            asset, quantity=-50, dt=dt, price=950.0,
            order_id=123, commission=None
        )
        position.update(transaction)
        self.assertEqual(position.quantity, 50)
        self.assertEqual(position.book_cost_ps, 960.0)
        self.assertEqual(position.direction, 1.0)
        self.assertEqual(position.current_trade_price, 950.0)
        self.assertEqual(position.market_value, 47500.0)
        self.assertEqual(position.unr_gain, -500.0)
        self.assertEqual(position.unr_perc_gain, -1.0416666666666665)

    def test_position_three_longs_one_short_one_long(self):
        """
        Tests that the quantity and book cost are
        correctly calculated for three long transactions,
        followed by a partial closing position, followed
        by a new long position, all in the same asset.
        
        Buy 100 qty at £1.00 -> £100
        Buy 100 qty at £2.00 -> £200
        Buy 200 qty at £3.00 -> £600
        Total qty after 3 longs is 400, with book cost £900 (£2.25 p/s)

        Sell 100 qty -> Book cost now £675 (25% holdings reduced),
        still at £2.25 p/s
        Buy 100 at £4.00 -> 400
        Final qty is 400, but book cost is now £1,075 (£2.6875 p/s).
        """
        asset = EquityMock(1, exchange='NYSE')
        # Initial long
        position = Position(
            asset, quantity=100, book_cost_ps=1.0,
            current_trade_price=1.0
        )
        # Second long
        dt = pd.Timestamp('2015-05-06')
        transaction = Transaction(
            asset, quantity=100, dt=dt, price=2.0,
            order_id=123, commission=None
        )
        position.update(transaction)
        self.assertEqual(position.quantity, 200)
        self.assertEqual(position.book_cost_ps, 1.5)
        # Third long
        dt = pd.Timestamp('2015-05-07')
        transaction = Transaction(
            asset, quantity=200, dt=dt, price=3.0,
            order_id=123, commission=None
        )
        position.update(transaction)
        self.assertEqual(position.quantity, 400)
        self.assertEqual(position.book_cost_ps, 2.25)
        # First short
        dt = pd.Timestamp('2015-05-08')
        transaction = Transaction(
            asset, quantity=-100, dt=dt, price=3.5,
            order_id=123, commission=None
        )
        position.update(transaction)
        self.assertEqual(position.quantity, 300)
        self.assertEqual(position.book_cost_ps, 2.25)
        # Final long
        dt = pd.Timestamp('2015-05-09')
        transaction = Transaction(
            asset, quantity=100, dt=dt, price=4.0,
            order_id=123, commission=None
        )
        position.update(transaction)
        self.assertEqual(position.quantity, 400)
        self.assertEqual(position.book_cost_ps, 2.6875)
        self.assertEqual(position.direction, 1.0)
        self.assertEqual(position.current_trade_price, 4.0)
        self.assertEqual(position.market_value, 1600.0)
        self.assertEqual(position.unr_gain, 525.0)
        self.assertEqual(position.unr_perc_gain, 48.837209302325576)

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
        self.assertEqual(position.market_value, -192000.0)
        self.assertEqual(position.unr_gain, -1000.0)
        self.assertEqual(position.unr_perc_gain, -0.5235602094240838)

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
        self.assertEqual(position.market_value, 0.0)
        self.assertEqual(position.unr_gain, 0.0)
        self.assertEqual(position.unr_perc_gain, 0.0)

    def test_position_short_long_insufficient_cover(self):
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
        self.assertEqual(position.market_value, -48000.0)
        self.assertEqual(position.unr_gain, -500.0)
        self.assertEqual(position.unr_perc_gain, -1.0526315789473684)

    def test_position_short_long_excess_cover(self):
        """
        Tests that the quantity and book cost are
        correctly calculated for an initial short
        position with an additional long transaction
        in the same asset, where the long position
        is in excess of the short position.
        """
        asset = EquityMock(1, exchange='NYSE')
        position = Position(
            asset, quantity=-100, book_cost_ps=700.0,
            current_trade_price=700.0
        )
        dt = pd.Timestamp('2015-05-06')
        transaction = Transaction(
            asset, quantity=175, dt=dt, price=873.0,
            order_id=123, commission=None
        )
        position.update(transaction)
        self.assertEqual(position.quantity, 75)
        self.assertEqual(position.book_cost_ps, 873.0)
        self.assertEqual(position.direction, 1.0)
        self.assertEqual(position.current_trade_price, 873.0)
        self.assertEqual(position.market_value, 65475.0)
        self.assertEqual(position.unr_gain, 0.0)
        self.assertEqual(position.unr_perc_gain, 0.0)

    def test_position_short_goes_to_half(self):
        """
        Tests that the quantity and book cost are
        correctly calculated for an initial short
        position, where the share value goes to zero.
        This should be a percentage gain of 100%.
        """
        asset = EquityMock(1, exchange='NYSE')
        position = Position(
            asset, quantity=-100, book_cost_ps=50.0,
            current_trade_price=50.0
        )
        dt = pd.Timestamp('2015-05-06')
        position.current_trade_price = 25.0
        position.current_trade_date = dt
        self.assertEqual(position.quantity, -100)
        self.assertEqual(position.book_cost_ps, 50.0)
        self.assertEqual(position.direction, -1.0)
        self.assertEqual(position.current_trade_price, 25.0)
        self.assertEqual(position.market_value, -2500.0)
        self.assertEqual(position.unr_gain, 2500.0)
        self.assertEqual(position.unr_perc_gain, 50.0)

    def test_position_short_goes_to_zero(self):
        """
        Tests that the quantity and book cost are
        correctly calculated for an initial short
        position, where the share value goes to zero.
        This should be a percentage gain of 100%.
        """
        asset = EquityMock(1, exchange='NYSE')
        position = Position(
            asset, quantity=-100, book_cost_ps=50.0,
            current_trade_price=50.0
        )
        dt = pd.Timestamp('2015-05-06')
        position.current_trade_price = 0.0
        position.current_trade_date = dt
        self.assertEqual(position.quantity, -100)
        self.assertEqual(position.book_cost_ps, 50.0)
        self.assertEqual(position.direction, -1.0)
        self.assertEqual(position.current_trade_price, 0.0)
        self.assertEqual(position.market_value, 0.0)
        self.assertEqual(position.unr_gain, 5000.0)
        self.assertEqual(position.unr_perc_gain, 100.0)

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

    def test_update_book_cost_for_commission_zero_position(self):
        """
        Tests that 'update_book_cost_for_commission' returns None
        when some positive commission is provided, given that the
        Position itself has zero quantity.
        """
        asset = EquityMock(1, exchange='NYSE')
        position = Position(
            asset, quantity=0, book_cost_ps=0.0, current_trade_price=0.0
        )
        self.assertEqual(
            position.update_book_cost_for_commission(asset, 15.0),
            None
        )

    def test_update_book_cost_for_commission_some_commission(self):
        """
        Tests that 'update_book_cost_for_commission' calculates
        book cost correctly for the position when a positive
        commission is supplied.
        """
        asset = EquityMock(1, exchange='NYSE')
        position = Position(
            asset, quantity=100, book_cost_ps=50.0, 
            current_trade_price=50.0
        )
        position.update_book_cost_for_commission(asset, 15.0)
        self.assertEqual(position.book_cost_ps, 50.15)
        self.assertEqual(position.book_cost, 5015.0)


if __name__ == "__main__":
    unittest.main()
