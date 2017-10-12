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
import unittest

import pandas as pd

from qstrader.broker.position_handler import PositionHandler
from qstrader.broker.transaction import Transaction


class EquityMock(object):
    """Mock object for the Asset-derived Equity class."""

    def __init__(self, asset_id, exchange=None):
        self.__name__ = "Equity"
        self.asset_id = asset_id
        self.exchange = exchange

    def __str__(self):
        return "%s(%s)" % (self.__name__, self.asset_id)


class PositionHandlerTests(unittest.TestCase):
    """Tests the PositionHandler class. Checks that the
    positions are correctly added. Checks that transacting
    in positions leads to the correct account values. Checks
    that the list of positions sums up to the correct market
    value, unrealised absolute gain and unrealised percentage
    gains.
    """

    def test_check_set_position_new_asset(self):
        """
        Checks the _check_set_position method when
        a new asset is added to the PositionHandler
        and when it is checked subsequently.
        """
        # Create PositionHandler, Asset and OrderedDict
        # positions list
        ph = PositionHandler()
        asset = EquityMock(1, exchange='NYSE')
        od = OrderedDict()
        self.assertEqual(ph.positions, od)

        # Check that the position is set for new asset
        pos = ph._check_set_position(asset)
        self.assertEqual(pos.asset, asset)

        # Check that the OrderedDict is correctly set
        # for new asset
        od[asset] = pos
        self.assertEqual(ph.positions, od)

        # Check that it works for a current asset
        pos = ph._check_set_position(asset)
        self.assertEqual(pos.asset, asset)
        self.assertEqual(ph.positions, od)

    def test_transact_position_new_position(self):
        """
        Tests the 'transact_position' method for a transaction
        with a brand new asset and checks that all objects are
        set correctly.
        """
        # Create the PositionHandler, Transaction and
        # carry out a transaction
        ph = PositionHandler()
        asset = EquityMock(1, exchange='NYSE')
        dt = pd.Timestamp('2015-05-06')
        transaction = Transaction(
            asset, quantity=100, dt=dt, price=960.0,
            order_id=123, commission=26.83
        )
        ph.transact_position(transaction)

        # Check that the position object is set correctly
        pos = ph.positions[asset]
        self.assertEqual(pos.quantity, 100)
        self.assertEqual(pos.direction, 1.0)
        self.assertEqual(pos.book_cost_ps, 960.2683000000001)
        self.assertEqual(pos.book_cost, 96026.83)

    def test_transact_position_current_position(self):
        """
        Tests the 'transact_position' method for a transaction
        with a current asset and checks that all objects are
        set correctly.
        """
        # Create the PositionHandler, Transaction and
        # carry out a transaction
        ph = PositionHandler()
        asset = EquityMock(1, exchange='NYSE')
        dt = pd.Timestamp('2015-05-06')
        transaction_long = Transaction(
            asset, quantity=100, dt=dt, price=960.0,
            order_id=123, commission=26.83
        )
        transaction_long_again = Transaction(
            asset, quantity=200, dt=dt, price=990.0,
            order_id=234, commission=18.53
        )
        ph.transact_position(transaction_long)
        ph.transact_position(transaction_long_again)

        # Check that the position object is set correctly
        pos = ph.positions[asset]
        self.assertEqual(pos.quantity, 300)
        self.assertEqual(pos.direction, 1.0)
        self.assertEqual(pos.book_cost_ps, 980.1512000000001)
        self.assertEqual(pos.book_cost, 294045.36000000004)

    def test_transact_position_quantity_zero(self):
        """
        Tests the 'transact_position' method for a transaction
        with net zero quantity after the transaction to ensure
        deletion of the position.
        """
        # Create the PositionHandler, Transaction and
        # carry out a transaction
        ph = PositionHandler()
        asset = EquityMock(1, exchange='NYSE')
        dt = pd.Timestamp('2015-05-06')
        transaction_long = Transaction(
            asset, quantity=100, dt=dt, price=960.0,
            order_id=123, commission=26.83
        )
        transaction_close = Transaction(
            asset, quantity=-100, dt=dt, price=980.0,
            order_id=234, commission=18.53
        )

        # Go long and then close, then check that the
        # positions OrderedDict is empty
        ph.transact_position(transaction_long)
        ph.transact_position(transaction_close)
        od = OrderedDict()
        self.assertEqual(ph.positions, od)

    def test_total_values_for_no_transactions(self):
        """
        Tests 'total_book_cost', 'total_market_value',
        'total_gain' and 'total_perc_gain' for the case
        of no transactions being carried out.
        """
        ph = PositionHandler()
        self.assertEqual(ph.total_book_cost(), 0.0)
        self.assertEqual(ph.total_market_value(), 0.0)
        self.assertEqual(ph.total_unr_gain(), 0.0)
        self.assertEqual(ph.total_unr_perc_gain(), 0.0)

    def test_total_values_for_two_separate_transactions(self):
        """
        Tests 'total_book_cost', 'total_market_value',
        'total_gain' and 'total_perc_gain' for single
        transactions in two separate assets.
        """
        ph = PositionHandler()
        # Asset 1
        asset1 = EquityMock(1, exchange='NYSE')
        dt1 = pd.Timestamp('2015-05-06')
        trans_pos_1 = Transaction(
            asset1, quantity=75, dt=dt1, price=483.45,
            order_id=1, commission=15.97
        )
        ph.transact_position(trans_pos_1)
        # Asset 2
        asset2 = EquityMock(2, exchange='NYSE')
        dt2 = pd.Timestamp('2015-05-07')
        trans_pos_2 = Transaction(
            asset2, quantity=250, dt=dt2, price=142.58,
            order_id=2, commission=8.35
        )
        ph.transact_position(trans_pos_2)
        # Check all total values
        self.assertEqual(ph.total_book_cost(), 71928.07)
        self.assertEqual(ph.total_market_value(), 71903.75)
        self.assertEqual(ph.total_unr_gain(), -24.31999999999971)
        self.assertEqual(ph.total_unr_perc_gain(), -0.03381155646190282)

    def test_update_commission(self):
        """
        Tests the 'update_commission' method to ensure
        commission is correctly set on the Position entities.
        """
        ph = PositionHandler()
        # Asset 1
        asset1 = EquityMock(1, exchange='NYSE')
        dt1 = pd.Timestamp('2015-05-06')
        trans_pos_1 = Transaction(
            asset1, quantity=75, dt=dt1, price=483.45,
            order_id=1, commission=0.0
        )
        ph.transact_position(trans_pos_1)
        ph.update_commission(asset1, 15.97)
        # Asset 2
        asset2 = EquityMock(2, exchange='NYSE')
        dt2 = pd.Timestamp('2015-05-07')
        trans_pos_2 = Transaction(
            asset2, quantity=250, dt=dt2, price=142.58,
            order_id=2, commission=0.0
        )
        ph.transact_position(trans_pos_2)
        ph.update_commission(asset2, 8.35)
        # Check all total values
        self.assertEqual(ph.total_book_cost(), 71928.07)
        self.assertEqual(ph.total_market_value(), 71903.75)
        self.assertEqual(ph.total_unr_gain(), -24.31999999999971)
        self.assertEqual(ph.total_unr_perc_gain(), -0.03381155646190282)

    def test_update_position_for_non_none_values(self):
        """
        Tests the 'update_position' method for non-None
        values when updating a Position entity.
        """
        ph = PositionHandler()
        # Asset 1
        asset1 = EquityMock(1, exchange='NYSE')
        dt1 = pd.Timestamp('2015-05-06')
        trans_pos_1 = Transaction(
            asset1, quantity=75, dt=dt1, price=483.45,
            order_id=1, commission=13.76
        )
        ph.transact_position(trans_pos_1)
        # Update values manually
        quantity=100
        current_trade_price=504.32
        current_trade_date=pd.Timestamp('2015-05-07')
        book_cost_ps=23.65
        ph.update_position(
            asset1,
            quantity=quantity,
            current_trade_price=current_trade_price,
            current_trade_date=current_trade_date,
            book_cost_ps=book_cost_ps
        )
        self.assertEqual(
            ph.positions[asset1].quantity,
            quantity
        )
        self.assertEqual(
            ph.positions[asset1].current_trade_price,
            current_trade_price
        )
        self.assertEqual(
            ph.positions[asset1].current_trade_date,
            current_trade_date
        )
        self.assertEqual(
            ph.positions[asset1].book_cost_ps,
            book_cost_ps
        )


if __name__ == "__main__":
    unittest.main()
