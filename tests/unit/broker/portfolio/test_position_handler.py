from collections import OrderedDict

import pandas as pd

from qstrader.asset.equity import Equity
from qstrader.broker.portfolio.position_handler import PositionHandler
from qstrader.broker.transaction.transaction import Transaction


def test_check_set_position_new_asset():
    """
    Checks the _check_set_position method when
    a new asset is added to the PositionHandler
    and when it is checked subsequently.
    """
    # Create PositionHandler, Asset and OrderedDict
    # positions list
    ph = PositionHandler()
    asset = Equity('Amazon, Inc.', 'AMZN')
    od = OrderedDict()
    assert ph.positions == od

    # Check that the position is set for new asset
    pos = ph._check_set_position(asset)
    assert pos.asset == asset

    # Check that the OrderedDict is correctly set
    # for new asset
    od[asset] = pos
    assert ph.positions == od

    # Check that it works for a current asset
    pos = ph._check_set_position(asset)
    assert pos.asset == asset
    assert ph.positions == od


def test_transact_position_new_position():
    """
    Tests the 'transact_position' method for a transaction
    with a brand new asset and checks that all objects are
    set correctly.
    """
    # Create the PositionHandler, Transaction and
    # carry out a transaction
    ph = PositionHandler()
    asset = Equity('Amazon, Inc.', 'AMZN')
    dt = pd.Timestamp('2015-05-06')
    transaction = Transaction(
        asset, quantity=100, dt=dt, price=960.0,
        order_id=123, commission=26.83
    )
    ph.transact_position(transaction)

    # Check that the position object is set correctly
    pos = ph.positions[asset]
    assert pos.quantity == 100
    assert pos.direction == 1.0
    assert pos.book_cost_pu == 960.2683000000001
    assert pos.book_cost == 96026.83


def test_transact_position_current_position():
    """
    Tests the 'transact_position' method for a transaction
    with a current asset and checks that all objects are
    set correctly.
    """
    # Create the PositionHandler, Transaction and
    # carry out a transaction
    ph = PositionHandler()
    asset = Equity('Amazon, Inc.', 'AMZN')
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
    assert pos.quantity == 300
    assert pos.direction == 1.0
    assert pos.book_cost_pu == 980.1512000000001
    assert pos.book_cost == 294045.36000000004


def test_transact_position_quantity_zero():
    """
    Tests the 'transact_position' method for a transaction
    with net zero quantity after the transaction to ensure
    deletion of the position.
    """
    # Create the PositionHandler, Transaction and
    # carry out a transaction
    ph = PositionHandler()
    asset = Equity('Amazon, Inc.', 'AMZN')
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
    assert ph.positions == od


def test_total_values_for_no_transactions():
    """
    Tests 'total_book_cost', 'total_market_value',
    'total_gain' and 'total_perc_gain' for the case
    of no transactions being carried out.
    """
    ph = PositionHandler()
    assert ph.total_book_cost() == 0.0
    assert ph.total_market_value() == 0.0
    assert ph.total_unrealised_gain() == 0.0
    assert ph.total_unrealised_percentage_gain() == 0.0


def test_total_values_for_two_separate_transactions():
    """
    Tests 'total_book_cost', 'total_market_value',
    'total_gain' and 'total_perc_gain' for single
    transactions in two separate assets.
    """
    ph = PositionHandler()

    # Asset 1
    asset1 = Equity('Amazon, Inc.', 'AMZN')
    dt1 = pd.Timestamp('2015-05-06')
    trans_pos_1 = Transaction(
        asset1, quantity=75, dt=dt1, price=483.45,
        order_id=1, commission=15.97
    )
    ph.transact_position(trans_pos_1)

    # Asset 2
    asset2 = Equity('Microsoft, Inc.', 'MSFT')
    dt2 = pd.Timestamp('2015-05-07')
    trans_pos_2 = Transaction(
        asset2, quantity=250, dt=dt2, price=142.58,
        order_id=2, commission=8.35
    )
    ph.transact_position(trans_pos_2)

    # Check all total values
    assert ph.total_book_cost() == 71928.07
    assert ph.total_market_value() == 71903.75
    assert ph.total_unrealised_gain() == -24.31999999999971
    assert ph.total_unrealised_percentage_gain() == -0.03381155646190282


def test_update_commission():
    """
    Tests the 'update_commission' method to ensure
    commission is correctly set on the Position entities.
    """
    ph = PositionHandler()

    # Asset 1
    asset1 = Equity('Amazon, Inc.', 'AMZN')
    dt1 = pd.Timestamp('2015-05-06')
    trans_pos_1 = Transaction(
        asset1, quantity=75, dt=dt1, price=483.45,
        order_id=1, commission=0.0
    )
    ph.transact_position(trans_pos_1)
    ph.update_commission(asset1, 15.97)

    # Asset 2
    asset2 = Equity('Microsoft, Inc.', 'MSFT')
    dt2 = pd.Timestamp('2015-05-07')
    trans_pos_2 = Transaction(
        asset2, quantity=250, dt=dt2, price=142.58,
        order_id=2, commission=0.0
    )
    ph.transact_position(trans_pos_2)
    ph.update_commission(asset2, 8.35)

    # Check all total values
    assert ph.total_book_cost() == 71928.07
    assert ph.total_market_value() == 71903.75
    assert ph.total_unrealised_gain() == -24.31999999999971
    assert ph.total_unrealised_percentage_gain() == -0.03381155646190282


def test_update_position_for_non_none_values():
    """
    Tests the 'update_position' method for non-None
    values when updating a Position entity.
    """
    ph = PositionHandler()

    # Asset 1
    asset1 = Equity('Amazon, Inc.', 'AMZN')
    dt1 = pd.Timestamp('2015-05-06')
    trans_pos_1 = Transaction(
        asset1, quantity=75, dt=dt1, price=483.45,
        order_id=1, commission=13.76
    )
    ph.transact_position(trans_pos_1)

    # Update values manually
    quantity = 100
    current_price = 504.32
    current_dt = pd.Timestamp('2015-05-07')
    book_cost_pu = 23.65
    ph.update_position(
        asset1,
        quantity=quantity,
        current_price=current_price,
        current_dt=current_dt,
        book_cost_pu=book_cost_pu
    )

    assert ph.positions[asset1].quantity == quantity
    assert ph.positions[asset1].current_price == current_price
    assert ph.positions[asset1].current_dt == current_dt
    assert ph.positions[asset1].book_cost_pu == book_cost_pu
