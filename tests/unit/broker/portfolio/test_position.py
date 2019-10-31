import pandas as pd
import pytest

from qstrader.asset.equity import Equity
from qstrader.broker.portfolio.position import Position
from qstrader.broker.transaction.transaction import Transaction


def test_position_representation():
    """
    Tests that the Position representation
    correctly recreates the object.
    """
    asset = Equity('Apple, Inc.', 'AAPL')
    position = Position(
        asset, quantity=153,
        book_cost_pu=950.0,
        current_price=950.0
    )
    exp_repr = (
        "Position(asset=Equity(name='Apple, Inc.', symbol='AAPL', tax_exempt=True), "
        "quantity=153, book_cost_pu=950.0, current_price=950.0)"
    )
    assert repr(position) == exp_repr


def test_position_long_twice():
    """
    Tests that the quantity and book cost are
    correctly calculated for an initial long
    position with an additional long transaction
    in the same asset.
    """
    asset = Equity('Apple, Inc.', 'AAPL')
    position = Position(
        asset,
        quantity=100,
        book_cost_pu=950.0,
        current_price=950.0
    )
    
    dt = pd.Timestamp('2015-05-06')
    transaction = Transaction(
        asset,
        quantity=100,
        dt=dt,
        price=960.0,
        order_id=123,
        commission=None
    )
    position.update(transaction)
    
    assert position.quantity == 200
    assert position.book_cost_pu == 955.0
    assert position.direction == 1.0
    assert position.current_price == 960.0
    assert position.market_value == 192000.0
    assert position.unrealised_gain == 1000.0
    assert position.unrealised_percentage_gain == 0.5235602094240838


def test_position_long_close():
    """
    Tests that the quantity and book cost are
    correctly calculated for an initial long
    position with an additional short transaction
    in the same asset, where the short closes
    the position.
    """
    asset = Equity('Apple, Inc.', 'AAPL')
    position = Position(
        asset,
        quantity=100,
        book_cost_pu=950.0,
        current_price=950.0
    )

    dt = pd.Timestamp('2015-05-06')
    transaction = Transaction(
        asset, quantity=-100, dt=dt, price=960.0,
        order_id=123, commission=None
    )
    position.update(transaction)
    
    assert position.quantity == 0
    assert position.book_cost_pu == 0.0
    assert position.direction == 1.0
    assert position.current_price == 960.0
    assert position.market_value == 0.0
    assert position.unrealised_gain == 0.0
    assert position.unrealised_percentage_gain == 0.0


def test_position_long_short_positive_gain():
    """
    Tests that the quantity and book cost are
    correctly calculated for an initial long
    position with an additional short transaction
    in the same asset, where the short does not
    completely eliminate the position and the
    result is a gain.
    """
    asset = Equity('Apple, Inc.', 'AAPL')
    position = Position(
        asset,
        quantity=100,
        book_cost_pu=950.0,
        current_price=950.0
    )

    dt = pd.Timestamp('2015-05-06')
    transaction = Transaction(
        asset,
        quantity=-50,
        dt=dt,
        price=960.0,
        order_id=123,
        commission=None
    )
    position.update(transaction)

    assert position.quantity == 50
    assert position.book_cost_pu == 950.0
    assert position.direction == 1.0
    assert position.current_price == 960.0
    assert position.market_value == 48000.0
    assert position.unrealised_gain == 500.0
    assert position.unrealised_percentage_gain == 1.0526315789473684


def test_position_long_short_negative_gain():
    """
    Tests that the quantity and book cost are
    correctly calculated for an initial long
    position with an additional short transaction
    in the same asset, where the short does not
    completely eliminate the position and the
    result is a loss.
    """
    asset = Equity('Apple, Inc.', 'AAPL')
    position = Position(
        asset,
        quantity=100,
        book_cost_pu=960.0,
        current_price=950.0
    )
    
    dt = pd.Timestamp('2015-05-06')
    transaction = Transaction(
        asset,
        quantity=-50,
        dt=dt,
        price=950.0,
        order_id=123,
        commission=None
    )
    position.update(transaction)
    
    assert position.quantity == 50
    assert position.book_cost_pu == 960.0
    assert position.direction == 1.0
    assert position.current_price == 950.0
    assert position.market_value == 47500.0
    assert position.unrealised_gain == -500.0
    assert position.unrealised_percentage_gain == -1.0416666666666665


def test_position_three_longs_one_short_one_long():
    """
    Tests that the quantity and book cost are
    correctly calculated for three long transactions,
    followed by a partial closing position, followed
    by a new long position, all in the same asset.

    Buy 100 qty at £1.00 -> £100
    Buy 100 qty at £2.00 -> £200
    Buy 200 qty at £3.00 -> £600
    Total qty after 3 longs is 400, with book cost £900 (£2.25 p/u)

    Sell 100 qty -> Book cost now £675 (25% holdings reduced),
    still at £2.25 p/u
    Buy 100 at £4.00 -> 400
    Final qty is 400, but book cost is now £1,075 (£2.6875 p/u).
    """
    asset = Equity('Apple, Inc.', 'AAPL')
    
    # Initial long
    position = Position(
        asset,
        quantity=100,
        book_cost_pu=1.0,
        current_price=1.0
    )
    
    # Second long
    dt = pd.Timestamp('2015-05-06')
    transaction = Transaction(
        asset,
        quantity=100,
        dt=dt,
        price=2.0,
        order_id=123,
        commission=None
    )
    position.update(transaction)
    assert position.quantity == 200
    assert position.book_cost_pu == 1.5
    
    # Third long
    dt = pd.Timestamp('2015-05-07')
    transaction = Transaction(
        asset,
        quantity=200,
        dt=dt,
        price=3.0,
        order_id=123,
        commission=None
    )
    position.update(transaction)
    assert position.quantity == 400
    assert position.book_cost_pu == 2.25
    
    # First short
    dt = pd.Timestamp('2015-05-08')
    transaction = Transaction(
        asset,
        quantity=-100,
        dt=dt,
        price=3.5,
        order_id=123,
        commission=None
    )
    position.update(transaction)
    assert position.quantity == 300
    assert position.book_cost_pu == 2.25
    
    # Final long
    dt = pd.Timestamp('2015-05-09')
    transaction = Transaction(
        asset,
        quantity=100,
        dt=dt,
        price=4.0,
        order_id=123,
        commission=None
    )
    position.update(transaction)
    
    assert position.quantity == 400
    assert position.book_cost_pu == 2.6875
    assert position.direction == 1.0
    assert position.current_price == 4.0
    assert position.market_value == 1600.0
    assert position.unrealised_gain == 525.0
    assert position.unrealised_percentage_gain == 48.837209302325576


def test_position_short_twice():
    """
    Tests that the quantity and book cost are
    correctly calculated for an initial short
    position with an additional short transaction
    in the same asset.
    """
    asset = Equity('Apple, Inc.', 'AAPL')
    position = Position(
        asset,
        quantity=-100,
        book_cost_pu=950.0,
        current_price=950.0
    )
    
    dt = pd.Timestamp('2015-05-06')
    transaction = Transaction(
        asset,
        quantity=-100,
        dt=dt,
        price=960.0,
        order_id=123,
        commission=None
    )
    position.update(transaction)
    
    assert position.quantity == -200
    assert position.book_cost_pu == 955.0
    assert position.direction == -1.0
    assert position.current_price == 960.0
    assert position.market_value == -192000.0
    assert position.unrealised_gain == -1000.0
    assert position.unrealised_percentage_gain == -0.5235602094240838


def test_position_short_close():
    """
    Tests that the quantity and book cost are
    correctly calculated for an initial short
    position with an additional long transaction
    in the same asset, where the long closes
    the position.
    """
    asset = Equity('Apple, Inc.', 'AAPL')
    position = Position(
        asset, quantity=-100, book_cost_pu=950.0,
        current_price=950.0
    )
    dt = pd.Timestamp('2015-05-06')
    transaction = Transaction(
        asset, quantity=100, dt=dt, price=960.0,
        order_id=123, commission=None
    )
    position.update(transaction)
    assert position.quantity == 0
    assert position.book_cost_pu == 0.0
    assert position.direction == 1.0
    assert position.current_price == 960.0
    assert position.market_value == 0.0
    assert position.unrealised_gain == 0.0
    assert position.unrealised_percentage_gain == 0.0


def test_position_short_long_insufficient_cover():
    """
    Tests that the quantity and book cost are
    correctly calculated for an initial short
    position with an additional long transaction
    in the same asset, where the long does not
    completely eliminate the position.
    """
    asset = Equity('Apple, Inc.', 'AAPL')
    position = Position(
        asset, quantity=-100, book_cost_pu=950.0,
        current_price=950.0
    )
    dt = pd.Timestamp('2015-05-06')
    transaction = Transaction(
        asset, quantity=50, dt=dt, price=960.0,
        order_id=123, commission=None
    )
    position.update(transaction)
    
    assert position.quantity == -50
    assert position.book_cost_pu == 950.0
    assert position.direction == -1.0
    assert position.current_price == 960.0
    assert position.market_value == -48000.0
    assert position.unrealised_gain == -500.0
    assert position.unrealised_percentage_gain == -1.0526315789473684


def test_position_short_long_excess_cover():
    """
    Tests that the quantity and book cost are
    correctly calculated for an initial short
    position with an additional long transaction
    in the same asset, where the long position
    is in excess of the short position.
    """
    asset = Equity('Apple, Inc.', 'AAPL')
    position = Position(
        asset, quantity=-100, book_cost_pu=700.0,
        current_price=700.0
    )
    dt = pd.Timestamp('2015-05-06')
    transaction = Transaction(
        asset, quantity=175, dt=dt, price=873.0,
        order_id=123, commission=None
    )
    position.update(transaction)
    
    assert position.quantity == 75
    assert position.book_cost_pu == 873.0
    assert position.direction == 1.0
    assert position.current_price == 873.0
    assert position.market_value == 65475.0
    assert position.unrealised_gain == 0.0
    assert position.unrealised_percentage_gain == 0.0


def test_position_short_goes_to_half():
    """
    Tests that the quantity and book cost are
    correctly calculated for an initial short
    position, where the share value goes to zero.
    This should be a percentage gain of 100%.
    """
    asset = Equity('Apple, Inc.', 'AAPL')
    position = Position(
        asset, quantity=-100, book_cost_pu=50.0,
        current_price=50.0
    )
    dt = pd.Timestamp('2015-05-06')
    position.current_price = 25.0
    position.current_trade_date = dt
    
    assert position.quantity == -100
    assert position.book_cost_pu == 50.0
    assert position.direction == -1.0
    assert position.current_price == 25.0
    assert position.market_value == -2500.0
    assert position.unrealised_gain == 2500.0
    assert position.unrealised_percentage_gain == 50.0


def test_position_short_goes_to_zero():
    """
    Tests that the quantity and book cost are
    correctly calculated for an initial short
    position, where the share value goes to zero.
    This should be a percentage gain of 100%.
    """
    asset = Equity('Apple, Inc.', 'AAPL')
    position = Position(
        asset, quantity=-100, book_cost_pu=50.0,
        current_price=50.0
    )
    dt = pd.Timestamp('2015-05-06')
    position.current_price = 0.0
    position.current_trade_date = dt
    
    assert position.quantity == -100
    assert position.book_cost_pu == 50.0
    assert position.direction == -1.0
    assert position.current_price == 0.0
    assert position.market_value == 0.0
    assert position.unrealised_gain == 5000.0
    assert position.unrealised_percentage_gain == 100.0


def test_update_for_incorrect_asset():
    """
    Tests that the 'update' method, when provided
    with a transaction with an asset that does not
    match the position's asset, raises an Exception.
    """
    asset1 = Equity('Apple, Inc.', 'AAPL')
    asset2 = Equity('Amazon, Inc.', 'AMZN')

    position = Position(
        asset1, quantity=100, book_cost_pu=950.0,
        current_price=950.0
    )
    dt = pd.Timestamp('2015-05-06')
    transaction = Transaction(
        asset2, quantity=50, dt=dt, price=960.0,
        order_id=123, commission=None
    )
    
    with pytest.raises(Exception):
        position.update(transaction)


def test_update_book_cost_for_commission_for_incorrect_asset():
    """
    Tests that the 'update_book_cost_for_commission'
    method, when provided with a transaction with an
    asset that does not match the position's asset,
    raises an Exception.
    """
    asset1 = Equity('Apple, Inc.', 'AAPL')
    asset2 = Equity('Amazon, Inc.', 'AMZN')

    position = Position(
        asset1, quantity=100, book_cost_pu=950.0,
        current_price=950.0
    )
    
    with pytest.raises(Exception):
        position.update_book_cost_for_commission(asset2, 23.00)


def test_update_book_cost_for_commission_for_no_commission():
    """
    Tests that 'update_book_cost_for_commission' returns None
    when zero or None commission is provided.
    """
    asset = Equity('Apple, Inc.', 'AAPL')
    position = Position(
        asset, quantity=100, book_cost_pu=950.0,
        current_price=950.0
    )
    
    assert position.update_book_cost_for_commission(asset, 0.0) is None
    assert position.update_book_cost_for_commission(asset, None) is None


def test_update_book_cost_for_commission_zero_position():
    """
    Tests that 'update_book_cost_for_commission' returns None
    when some positive commission is provided, given that the
    Position itself has zero quantity.
    """
    asset = Equity('Apple, Inc.', 'AAPL')
    position = Position(
        asset, quantity=0, book_cost_pu=0.0, current_price=0.0
    )
    assert position.update_book_cost_for_commission(asset, 15.0) is None


def test_update_book_cost_for_commission_some_commission():
    """
    Tests that 'update_book_cost_for_commission' calculates
    book cost correctly for the position when a positive
    commission is supplied.
    """
    asset = Equity('Apple, Inc.', 'AAPL')
    position = Position(
        asset, quantity=100, book_cost_pu=50.0,
        current_price=50.0
    )
    position.update_book_cost_for_commission(asset, 15.0)
    
    assert position.book_cost_pu == 50.15
    assert position.book_cost == 5015.0
