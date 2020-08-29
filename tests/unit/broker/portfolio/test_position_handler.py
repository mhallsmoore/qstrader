from collections import OrderedDict

import numpy as np
import pandas as pd
import pytz

from qstrader.broker.portfolio.position_handler import PositionHandler
from qstrader.broker.transaction.transaction import Transaction


def test_transact_position_new_position():
    """
    Tests the 'transact_position' method for a transaction
    with a brand new asset and checks that all objects are
    set correctly.
    """
    # Create the PositionHandler, Transaction and
    # carry out a transaction
    ph = PositionHandler()
    asset = 'EQ:AMZN'

    transaction = Transaction(
        asset,
        quantity=100,
        dt=pd.Timestamp('2015-05-06 15:00:00', tz=pytz.UTC),
        price=960.0,
        order_id=123,
        commission=26.83
    )
    ph.transact_position(transaction)

    # Check that the position object is set correctly
    pos = ph.positions[asset]

    assert pos.buy_quantity == 100
    assert pos.sell_quantity == 0
    assert pos.net_quantity == 100
    assert pos.direction == 1
    assert pos.avg_price == 960.2683000000001


def test_transact_position_current_position():
    """
    Tests the 'transact_position' method for a transaction
    with a current asset and checks that all objects are
    set correctly.
    """
    # Create the PositionHandler, Transaction and
    # carry out a transaction
    ph = PositionHandler()
    asset = 'EQ:AMZN'
    dt = pd.Timestamp('2015-05-06 15:00:00', tz=pytz.UTC)
    new_dt = pd.Timestamp('2015-05-06 16:00:00', tz=pytz.UTC)

    transaction_long = Transaction(
        asset,
        quantity=100,
        dt=dt,
        price=960.0,
        order_id=123,
        commission=26.83
    )
    ph.transact_position(transaction_long)

    transaction_long_again = Transaction(
        asset,
        quantity=200,
        dt=new_dt,
        price=990.0,
        order_id=234,
        commission=18.53
    )
    ph.transact_position(transaction_long_again)

    # Check that the position object is set correctly
    pos = ph.positions[asset]

    assert pos.buy_quantity == 300
    assert pos.sell_quantity == 0
    assert pos.net_quantity == 300
    assert pos.direction == 1
    assert np.isclose(pos.avg_price, 980.1512)


def test_transact_position_quantity_zero():
    """
    Tests the 'transact_position' method for a transaction
    with net zero quantity after the transaction to ensure
    deletion of the position.
    """
    # Create the PositionHandler, Transaction and
    # carry out a transaction
    ph = PositionHandler()
    asset = 'EQ:AMZN'
    dt = pd.Timestamp('2015-05-06 15:00:00', tz=pytz.UTC)
    new_dt = pd.Timestamp('2015-05-06 16:00:00', tz=pytz.UTC)

    transaction_long = Transaction(
        asset,
        quantity=100,
        dt=dt,
        price=960.0,
        order_id=123, commission=26.83
    )
    ph.transact_position(transaction_long)

    transaction_close = Transaction(
        asset,
        quantity=-100,
        dt=new_dt,
        price=980.0,
        order_id=234,
        commission=18.53
    )
    ph.transact_position(transaction_close)

    # Go long and then close, then check that the
    # positions OrderedDict is empty
    assert ph.positions == OrderedDict()


def test_total_values_for_no_transactions():
    """
    Tests 'total_market_value', 'total_unrealised_pnl',
    'total_realised_pnl' and 'total_pnl' for the case
    of no transactions being carried out.
    """
    ph = PositionHandler()
    assert ph.total_market_value() == 0.0
    assert ph.total_unrealised_pnl() == 0.0
    assert ph.total_realised_pnl() == 0.0
    assert ph.total_pnl() == 0.0


def test_total_values_for_two_separate_transactions():
    """
    Tests 'total_market_value', 'total_unrealised_pnl',
    'total_realised_pnl' and 'total_pnl' for single
    transactions in two separate assets.
    """
    ph = PositionHandler()

    # Asset 1
    asset1 = 'EQ:AMZN'
    dt1 = pd.Timestamp('2015-05-06 15:00:00', tz=pytz.UTC)
    trans_pos_1 = Transaction(
        asset1,
        quantity=75,
        dt=dt1,
        price=483.45,
        order_id=1,
        commission=15.97
    )
    ph.transact_position(trans_pos_1)

    # Asset 2
    asset2 = 'EQ:MSFT'
    dt2 = pd.Timestamp('2015-05-07 15:00:00', tz=pytz.UTC)
    trans_pos_2 = Transaction(
        asset2,
        quantity=250,
        dt=dt2,
        price=142.58,
        order_id=2,
        commission=8.35
    )
    ph.transact_position(trans_pos_2)

    # Check all total values
    assert ph.total_market_value() == 71903.75
    assert np.isclose(ph.total_unrealised_pnl(), -24.31999999999971)
    assert ph.total_realised_pnl() == 0.0
    assert np.isclose(ph.total_pnl(), -24.31999999999971)
