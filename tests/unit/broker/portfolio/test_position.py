import numpy as np
import pandas as pd
import pytest
import pytz

from qstrader.broker.portfolio.position import Position
from qstrader.broker.transaction.transaction import Transaction


def test_basic_long_equities_position():
    """
    Tests that the properties on the Position
    are calculated for a simple long equities position.
    """
    # Initial long details
    asset = 'EQ:MSFT'
    quantity = 100
    dt = pd.Timestamp('2020-06-16 15:00:00', tz=pytz.UTC)
    price = 193.74
    order_id = 123
    commission = 1.0

    # Create the initial transaction and position
    transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position = Position.open_from_transaction(transaction)

    assert position.asset == asset
    assert position.current_price == price
    assert position.current_dt == dt

    # Update the market price
    new_market_price = 192.80
    new_dt = pd.Timestamp('2020-06-16 16:00:00', tz=pytz.UTC)
    position.update_current_price(new_market_price, new_dt)

    assert position.current_price == new_market_price
    assert position.current_dt == new_dt

    assert position.buy_quantity == 100
    assert position.sell_quantity == 0
    assert position.avg_bought == 193.74
    assert position.avg_sold == 0.0
    assert position.commission == 1.0

    assert position.direction == 1
    assert position.market_value == 19280.0
    assert position.avg_price == 193.75
    assert position.net_quantity == 100
    assert position.total_bought == 19374.0
    assert position.total_sold == 0.0
    assert position.net_total == -19374.0
    assert position.net_incl_commission == -19375.0
    assert np.isclose(position.unrealised_pnl, -95.0)
    assert np.isclose(position.realised_pnl, 0.0)


def test_position_long_twice():
    """
    Tests that the properties on the Position
    are calculated for two consective long trades
    with differing quantities and market prices.
    """
    # Initial long details
    asset = 'EQ:MSFT'
    quantity = 100
    dt = pd.Timestamp('2020-06-16 15:00:00', tz=pytz.UTC)
    price = 193.74
    order_id = 123
    commission = 1.0

    # Create the initial transaction and position
    first_transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position = Position.open_from_transaction(first_transaction)

    assert position.asset == asset
    assert position.current_price == price
    assert position.current_dt == dt

    # Second long
    second_quantity = 60
    second_dt = pd.Timestamp('2020-06-16 16:00:00', tz=pytz.UTC)
    second_price = 193.79
    second_order_id = 234
    second_commission = 1.0
    second_transaction = Transaction(
        asset,
        quantity=second_quantity,
        dt=second_dt,
        price=second_price,
        order_id=second_order_id,
        commission=second_commission
    )
    position.transact(second_transaction)

    assert position.current_price == second_price
    assert position.current_dt == second_dt

    assert position.buy_quantity == 160
    assert position.sell_quantity == 0
    assert np.isclose(position.avg_bought, 193.75875)
    assert position.avg_sold == 0.0
    assert position.commission == 2.0

    assert position.direction == 1
    assert np.isclose(position.market_value, 31006.40)
    assert position.avg_price == 193.77125
    assert position.net_quantity == 160
    assert position.total_bought == 31001.40
    assert position.total_sold == 0.0
    assert position.net_total == -31001.40
    assert position.net_incl_commission == -31003.40
    assert np.isclose(position.unrealised_pnl, 3.0)
    assert np.isclose(position.realised_pnl, 0.0)


def test_position_long_close():
    """
    Tests that the properties on the Position
    are calculated for a long opening trade and
    subsequent closing trade.
    """
    # Initial long details
    asset = 'EQ:AMZN'
    quantity = 100
    dt = pd.Timestamp('2020-06-16 15:00:00', tz=pytz.UTC)
    price = 2615.27
    order_id = 123
    commission = 1.0

    # Create the initial transaction and position
    first_transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position = Position.open_from_transaction(first_transaction)

    assert position.asset == asset
    assert position.current_price == price
    assert position.current_dt == dt

    # Closing trade
    second_quantity = -100
    second_dt = pd.Timestamp('2020-06-16 16:00:00', tz=pytz.UTC)
    second_price = 2622.0
    second_order_id = 234
    second_commission = 6.81
    second_transaction = Transaction(
        asset,
        quantity=second_quantity,
        dt=second_dt,
        price=second_price,
        order_id=second_order_id,
        commission=second_commission
    )
    position.transact(second_transaction)

    assert position.current_price == second_price
    assert position.current_dt == second_dt

    assert position.buy_quantity == 100
    assert position.sell_quantity == 100
    assert position.avg_bought == 2615.27
    assert position.avg_sold == 2622.0
    assert position.commission == 7.81

    assert position.direction == 0
    assert position.market_value == 0.0
    assert position.avg_price == 0.0
    assert position.net_quantity == 0
    assert position.total_bought == 261527.0
    assert position.total_sold == 262200.0
    assert position.net_total == 673.0
    assert position.net_incl_commission == 665.19
    assert position.unrealised_pnl == 0.0
    assert position.realised_pnl == 665.19


def test_position_long_and_short():
    """
    Tests that the properties on the Position
    are calculated for a long trade followed by
    a partial closing short trade with differing
    market prices.
    """
    # Initial long details
    asset = 'EQ:SPY'
    quantity = 100
    dt = pd.Timestamp('2020-06-16 15:00:00', tz=pytz.UTC)
    price = 307.05
    order_id = 123
    commission = 1.0

    # Create the initial transaction and position
    first_transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position = Position.open_from_transaction(first_transaction)

    assert position.asset == asset
    assert position.current_price == price
    assert position.current_dt == dt

    # Short details and transaction
    second_quantity = -60
    second_dt = pd.Timestamp('2020-06-16 16:00:00', tz=pytz.UTC)
    second_price = 314.91
    second_order_id = 234
    second_commission = 1.42
    second_transaction = Transaction(
        asset,
        quantity=second_quantity,
        dt=second_dt,
        price=second_price,
        order_id=second_order_id,
        commission=second_commission
    )
    position.transact(second_transaction)

    assert position.current_price == second_price
    assert position.current_dt == second_dt

    assert position.buy_quantity == 100
    assert position.sell_quantity == 60
    assert position.avg_bought == 307.05
    assert position.avg_sold == 314.91
    assert position.commission == 2.42

    assert position.direction == 1
    assert np.isclose(position.market_value, 12596.40)
    assert position.avg_price == 307.06
    assert position.net_quantity == 40
    assert position.total_bought == 30705.0
    assert np.isclose(position.total_sold, 18894.60)
    assert np.isclose(position.net_total, -11810.40)
    assert np.isclose(position.net_incl_commission, -11812.82)
    assert np.isclose(position.unrealised_pnl, 314.0)
    assert np.isclose(position.realised_pnl, 469.58)


def test_position_long_short_long_short_ending_long():
    """
    Tests that the properties on the Position
    are calculated for four trades consisting
    of a long, short, long and short, net long
    after all trades with varying quantities
    and market prices.
    """
    # First trade (first long)
    asset = 'EQ:SPY'
    quantity = 453
    dt = pd.Timestamp('2020-06-16 15:00:00', tz=pytz.UTC)
    price = 312.96
    order_id = 100
    commission = 1.95

    # Create the initial transaction and position
    first_transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position = Position.open_from_transaction(first_transaction)

    # Second trade (first short)
    quantity = -397
    dt = pd.Timestamp('2020-06-16 16:00:00', tz=pytz.UTC)
    price = 315.599924
    order_id = 101
    commission = 4.8
    transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position.transact(transaction)

    # Third trade (second long)
    quantity = 624
    dt = pd.Timestamp('2020-06-16 17:00:00', tz=pytz.UTC)
    price = 312.96
    order_id = 102
    commission = 2.68
    transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position.transact(transaction)

    # Fourth trade (second short), now net long
    quantity = -519
    dt = pd.Timestamp('2020-06-16 18:00:00', tz=pytz.UTC)
    price = 315.78
    order_id = 103
    commission = 6.28
    transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position.transact(transaction)

    assert position.asset == asset
    assert position.current_price == price
    assert position.current_dt == dt

    assert position.buy_quantity == 1077
    assert position.sell_quantity == 916
    assert position.avg_bought == 312.96
    assert position.avg_sold == 315.70195396069863
    assert position.commission == 15.71

    assert position.direction == 1
    assert np.isclose(position.market_value, 50840.58)
    assert position.avg_price == 312.96429897864436
    assert position.net_quantity == 161
    assert position.total_bought == 337057.92
    assert np.isclose(position.total_sold, 289182.99)
    assert np.isclose(position.net_total, -47874.93)
    assert np.isclose(position.net_incl_commission, -47890.64)
    assert np.isclose(position.unrealised_pnl, 453.327864438)
    assert np.isclose(position.realised_pnl, 2496.61)


def test_basic_short_equities_position():
    """
    Tests that the properties on the Position
    are calculated for a simple short equities position.
    """
    # Initial short details
    asset = 'EQ:TLT'
    quantity = -100
    dt = pd.Timestamp('2020-06-16 15:00:00', tz=pytz.UTC)
    price = 162.39
    order_id = 123
    commission = 1.37

    # Create the initial transaction and position
    transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position = Position.open_from_transaction(transaction)

    assert position.asset == asset
    assert position.current_price == price
    assert position.current_dt == dt

    # Update the market price
    new_market_price = 159.43
    new_dt = pd.Timestamp('2020-06-16 16:00:00', tz=pytz.UTC)
    position.update_current_price(new_market_price, new_dt)

    assert position.current_price == new_market_price
    assert position.current_dt == new_dt

    assert position.buy_quantity == 0
    assert position.sell_quantity == 100
    assert position.avg_bought == 0.0
    assert position.avg_sold == 162.39
    assert position.commission == 1.37

    assert position.direction == -1
    assert position.market_value == -15943.0
    assert position.avg_price == 162.3763
    assert position.net_quantity == -100
    assert position.total_bought == 0.0

    # np.isclose used for floating point precision
    assert np.isclose(position.total_sold, 16239.0)
    assert np.isclose(position.net_total, 16239.0)
    assert np.isclose(position.net_incl_commission, 16237.63)
    assert np.isclose(position.unrealised_pnl, 294.63)
    assert np.isclose(position.realised_pnl, 0.0)


def test_position_short_twice():
    """
    Tests that the properties on the Position
    are calculated for two consective short trades
    with differing quantities and market prices.
    """
    # Initial short details
    asset = 'EQ:MSFT'
    quantity = -100
    dt = pd.Timestamp('2020-06-16 15:00:00', tz=pytz.UTC)
    price = 194.55
    order_id = 123
    commission = 1.44

    # Create the initial transaction and position
    first_transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position = Position.open_from_transaction(first_transaction)

    assert position.asset == asset
    assert position.current_price == price
    assert position.current_dt == dt

    # Second short
    second_quantity = -60
    second_dt = pd.Timestamp('2020-06-16 16:00:00', tz=pytz.UTC)
    second_price = 194.76
    second_order_id = 234
    second_commission = 1.27
    second_transaction = Transaction(
        asset,
        quantity=second_quantity,
        dt=second_dt,
        price=second_price,
        order_id=second_order_id,
        commission=second_commission
    )
    position.transact(second_transaction)

    assert position.current_price == second_price
    assert position.current_dt == second_dt

    assert position.buy_quantity == 0
    assert position.sell_quantity == 160
    assert position.avg_bought == 0.0
    assert position.avg_sold == 194.62875
    assert position.commission == 2.71

    assert position.direction == -1
    assert np.isclose(position.market_value, -31161.6)
    assert np.isclose(position.avg_price, 194.6118125)
    assert position.net_quantity == -160
    assert position.total_bought == 0.0
    assert position.total_sold == 31140.60
    assert position.net_total == 31140.6
    assert position.net_incl_commission == 31137.89
    assert np.isclose(position.unrealised_pnl, -23.71)
    assert np.isclose(position.realised_pnl, 0.0)


def test_position_short_close():
    """
    Tests that the properties on the Position
    are calculated for a short opening trade and
    subsequent closing trade.
    """
    # Initial short details
    asset = 'EQ:TSLA'
    quantity = -100
    dt = pd.Timestamp('2020-06-16 15:00:00', tz=pytz.UTC)
    price = 982.13
    order_id = 123
    commission = 3.18

    # Create the initial transaction and position
    first_transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position = Position.open_from_transaction(first_transaction)

    assert position.asset == asset
    assert position.current_price == price
    assert position.current_dt == dt

    # Closing trade
    second_quantity = 100
    second_dt = pd.Timestamp('2020-06-16 16:00:00', tz=pytz.UTC)
    second_price = 982.13
    second_order_id = 234
    second_commission = 1.0
    second_transaction = Transaction(
        asset,
        quantity=second_quantity,
        dt=second_dt,
        price=second_price,
        order_id=second_order_id,
        commission=second_commission
    )
    position.transact(second_transaction)

    assert position.current_price == second_price
    assert position.current_dt == second_dt

    assert position.buy_quantity == 100
    assert position.sell_quantity == 100
    assert position.avg_bought == 982.13
    assert position.avg_sold == 982.13
    assert position.commission == 4.18

    assert position.direction == 0
    assert position.market_value == 0.0
    assert position.avg_price == 0.0
    assert position.net_quantity == 0
    assert position.total_bought == 98213.0
    assert position.total_sold == 98213.0
    assert position.net_total == 0.0
    assert position.net_incl_commission == -4.18
    assert position.unrealised_pnl == 0.0
    assert position.realised_pnl == -4.18


def test_position_short_and_long():
    """
    Tests that the properties on the Position
    are calculated for a short trade followed by
    a partial closing long trade with differing
    market prices.
    """
    # Initial short details
    asset = 'EQ:TLT'
    quantity = -100
    dt = pd.Timestamp('2020-06-16 15:00:00', tz=pytz.UTC)
    price = 162.39
    order_id = 123
    commission = 1.37

    # Create the initial transaction and position
    transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position = Position.open_from_transaction(transaction)

    assert position.asset == asset
    assert position.current_price == price
    assert position.current_dt == dt

    # Long details and transaction
    second_quantity = 60
    second_dt = pd.Timestamp('2020-06-16 16:00:00', tz=pytz.UTC)
    second_price = 159.99
    second_order_id = 234
    second_commission = 1.0
    second_transaction = Transaction(
        asset,
        quantity=second_quantity,
        dt=second_dt,
        price=second_price,
        order_id=second_order_id,
        commission=second_commission
    )
    position.transact(second_transaction)

    assert position.current_price == second_price
    assert position.current_dt == second_dt

    assert position.buy_quantity == 60
    assert position.sell_quantity == 100
    assert np.isclose(position.avg_bought, 159.99)
    assert position.avg_sold == 162.39
    assert position.commission == 2.37

    assert position.direction == -1
    assert np.isclose(position.market_value, -6399.6)
    assert position.avg_price == 162.3763
    assert position.net_quantity == -40
    assert np.isclose(position.total_bought, 9599.40)
    assert np.isclose(position.total_sold, 16239.0)
    assert np.isclose(position.net_total, 6639.60)
    assert np.isclose(position.net_incl_commission, 6637.23)
    assert np.isclose(position.unrealised_pnl, 95.452)
    assert np.isclose(position.realised_pnl, 142.1779999999)


def test_position_short_long_short_long_ending_short():
    """
    Tests that the properties on the Position
    are calculated for four trades consisting
    of a short, long, short and long ending net
    short after all trades with varying quantities
    and market prices.
    """
    # First trade (first short)
    asset = 'EQ:AGG'
    quantity = -762
    dt = pd.Timestamp('2020-06-16 15:00:00', tz=pytz.UTC)
    price = 117.74
    order_id = 100
    commission = 5.35
    transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position = Position.open_from_transaction(transaction)

    # Second trade (first long)
    quantity = 477
    dt = pd.Timestamp('2020-06-16 16:00:00', tz=pytz.UTC)
    price = 117.875597
    order_id = 101
    commission = 2.31
    transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position.transact(transaction)

    # Third trade (second short)
    quantity = -595
    dt = pd.Timestamp('2020-06-16 17:00:00', tz=pytz.UTC)
    price = 117.74
    order_id = 102
    commission = 4.18
    transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position.transact(transaction)

    # Fourth trade (second long), now net short
    quantity = 427
    dt = pd.Timestamp('2020-06-16 18:00:00', tz=pytz.UTC)
    price = 117.793115
    order_id = 103
    commission = 2.06
    transaction = Transaction(
        asset,
        quantity=quantity,
        dt=dt,
        price=price,
        order_id=order_id,
        commission=commission
    )
    position.transact(transaction)

    assert position.asset == asset
    assert position.current_price == price
    assert position.current_dt == dt

    assert position.buy_quantity == 904
    assert position.sell_quantity == 1357
    assert position.avg_bought == 117.83663702876107
    assert position.avg_sold == 117.74
    assert np.isclose(position.commission, 13.90)

    assert position.direction == -1
    assert np.isclose(position.market_value, -53360.281095)
    assert position.avg_price == 117.73297715549005
    assert position.net_quantity == -453
    assert position.total_bought == 106524.31987400001
    assert np.isclose(position.total_sold, 159773.18)
    assert np.isclose(position.net_total, 53248.86)
    assert np.isclose(position.net_incl_commission, 53234.95)
    assert np.isclose(position.unrealised_pnl, -27.242443563)
    assert np.isclose(position.realised_pnl, -98.0785254)


def test_transact_for_incorrect_asset():
    """
    Tests that the 'transact' method, when provided
    with a Transaction with an Asset that does not
    match the position's asset, raises an Exception.
    """
    asset1 = 'EQ:AAPL'
    asset2 = 'EQ:AMZN'

    position = Position(
        asset1,
        current_price=950.0,
        current_dt=pd.Timestamp('2020-06-16 15:00:00', tz=pytz.UTC),
        buy_quantity=100,
        sell_quantity=0,
        avg_bought=950.0,
        avg_sold=0.0,
        buy_commission=1.0,
        sell_commission=0.0
    )

    new_dt = pd.Timestamp('2020-06-16 16:00:00')
    transaction = Transaction(
        asset2,
        quantity=50,
        dt=new_dt,
        price=960.0,
        order_id=123,
        commission=1.0
    )

    with pytest.raises(Exception):
        position.update(transaction)
