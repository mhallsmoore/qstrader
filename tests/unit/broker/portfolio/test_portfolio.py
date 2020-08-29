import pandas as pd
import pytz
import pytest

from qstrader.broker.portfolio.portfolio import Portfolio
from qstrader.broker.portfolio.portfolio_event import PortfolioEvent
from qstrader.broker.transaction.transaction import Transaction


def test_initial_settings_for_default_portfolio():
    """
    Test that the initial settings are as they should be
    for two specified portfolios.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)

    # Test a default Portfolio
    port1 = Portfolio(start_dt)
    assert port1.start_dt == start_dt
    assert port1.current_dt == start_dt
    assert port1.currency == "USD"
    assert port1.starting_cash == 0.0
    assert port1.portfolio_id is None
    assert port1.name is None
    assert port1.total_market_value == 0.0
    assert port1.cash == 0.0
    assert port1.total_equity == 0.0

    # Test a Portfolio with keyword arguments
    port2 = Portfolio(
        start_dt, starting_cash=1234567.56, currency="USD",
        portfolio_id=12345, name="My Second Test Portfolio"
    )
    assert port2.start_dt == start_dt
    assert port2.current_dt == start_dt
    assert port2.currency == "USD"
    assert port2.starting_cash == 1234567.56
    assert port2.portfolio_id == 12345
    assert port2.name == "My Second Test Portfolio"
    assert port2.total_equity == 1234567.56
    assert port2.total_market_value == 0.0
    assert port2.cash == 1234567.56


def test_portfolio_currency_settings():
    """
    Test that USD and GBP currencies are correctly set with
    some currency keyword arguments and that the currency
    formatter produces the correct strings.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)

    # Test a US portfolio produces correct values
    cur1 = "USD"
    port1 = Portfolio(start_dt, currency=cur1)
    assert port1.currency == "USD"

    # Test a UK portfolio produces correct values
    cur2 = "GBP"
    port2 = Portfolio(start_dt, currency=cur2)
    assert port2.currency == "GBP"


def test_subscribe_funds_behaviour():
    """
    Test subscribe_funds raises for incorrect datetime
    Test subscribe_funds raises for negative amount
    Test subscribe_funds correctly adds positive
    amount, generates correct event and modifies time
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    earlier_dt = pd.Timestamp('2017-10-04 08:00:00', tz=pytz.UTC)
    later_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
    pos_cash = 1000.0
    neg_cash = -1000.0
    port = Portfolio(start_dt, starting_cash=2000.0)

    # Test subscribe_funds raises for incorrect datetime
    with pytest.raises(ValueError):
        port.subscribe_funds(earlier_dt, pos_cash)

    # Test subscribe_funds raises for negative amount
    with pytest.raises(ValueError):
        port.subscribe_funds(start_dt, neg_cash)

    # Test subscribe_funds correctly adds positive
    # amount, generates correct event and modifies time
    port.subscribe_funds(later_dt, pos_cash)

    assert port.cash == 3000.0
    assert port.total_market_value == 0.0
    assert port.total_equity == 3000.0

    pe1 = PortfolioEvent(
        dt=start_dt, type='subscription',
        description="SUBSCRIPTION", debit=0.0,
        credit=2000.0, balance=2000.0
    )
    pe2 = PortfolioEvent(
        dt=later_dt, type='subscription',
        description="SUBSCRIPTION", debit=0.0,
        credit=1000.0, balance=3000.0
    )

    assert port.history == [pe1, pe2]
    assert port.current_dt == later_dt


def test_withdraw_funds_behaviour():
    """
    Test withdraw_funds raises for incorrect datetime
    Test withdraw_funds raises for negative amount
    Test withdraw_funds raises for lack of cash
    Test withdraw_funds correctly subtracts positive
    amount, generates correct event and modifies time
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    earlier_dt = pd.Timestamp('2017-10-04 08:00:00', tz=pytz.UTC)
    later_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
    even_later_dt = pd.Timestamp('2017-10-07 08:00:00', tz=pytz.UTC)
    pos_cash = 1000.0
    neg_cash = -1000.0
    port_raise = Portfolio(start_dt)

    # Test withdraw_funds raises for incorrect datetime
    with pytest.raises(ValueError):
        port_raise.withdraw_funds(earlier_dt, pos_cash)

    # Test withdraw_funds raises for negative amount
    with pytest.raises(ValueError):
        port_raise.withdraw_funds(start_dt, neg_cash)

    # Test withdraw_funds raises for not enough cash
    port_broke = Portfolio(start_dt)
    port_broke.subscribe_funds(later_dt, 1000.0)

    with pytest.raises(ValueError):
        port_broke.withdraw_funds(later_dt, 2000.0)

    # Test withdraw_funds correctly subtracts positive
    # amount, generates correct event and modifies time
    # Initial subscribe
    port_cor = Portfolio(start_dt)
    port_cor.subscribe_funds(later_dt, pos_cash)
    pe_sub = PortfolioEvent(
        dt=later_dt, type='subscription',
        description="SUBSCRIPTION", debit=0.0,
        credit=1000.0, balance=1000.0
    )
    assert port_cor.cash == 1000.0
    assert port_cor.total_market_value == 0.0
    assert port_cor.total_equity == 1000.0
    assert port_cor.history == [pe_sub]
    assert port_cor.current_dt == later_dt

    # Now withdraw
    port_cor.withdraw_funds(even_later_dt, 468.0)
    pe_wdr = PortfolioEvent(
        dt=even_later_dt, type='withdrawal',
        description="WITHDRAWAL", debit=468.0,
        credit=0.0, balance=532.0
    )
    assert port_cor.cash == 532.0
    assert port_cor.total_market_value == 0.0
    assert port_cor.total_equity == 532.0
    assert port_cor.history == [pe_sub, pe_wdr]
    assert port_cor.current_dt == even_later_dt


def test_transact_asset_behaviour():
    """
    Test transact_asset raises for incorrect time
    Test correct total_cash and total_securities_value
    for correct transaction (commission etc), correct
    portfolio event and correct time update
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    earlier_dt = pd.Timestamp('2017-10-04 08:00:00', tz=pytz.UTC)
    later_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
    even_later_dt = pd.Timestamp('2017-10-07 08:00:00', tz=pytz.UTC)
    port = Portfolio(start_dt)
    asset = 'EQ:AAA'

    # Test transact_asset raises for incorrect time
    tn_early = Transaction(
        asset=asset,
        quantity=100,
        dt=earlier_dt,
        price=567.0,
        order_id=1,
        commission=0.0
    )
    with pytest.raises(ValueError):
        port.transact_asset(tn_early)

    # Test transact_asset raises for transaction total
    # cost exceeding total cash
    port.subscribe_funds(later_dt, 1000.0)

    assert port.cash == 1000.0
    assert port.total_market_value == 0.0
    assert port.total_equity == 1000.0

    pe_sub1 = PortfolioEvent(
        dt=later_dt, type='subscription',
        description="SUBSCRIPTION", debit=0.0,
        credit=1000.0, balance=1000.0
    )

    # Test correct total_cash and total_securities_value
    # for correct transaction (commission etc), correct
    # portfolio event and correct time update
    port.subscribe_funds(even_later_dt, 99000.0)

    assert port.cash == 100000.0
    assert port.total_market_value == 0.0
    assert port.total_equity == 100000.0

    pe_sub2 = PortfolioEvent(
        dt=even_later_dt, type='subscription',
        description="SUBSCRIPTION", debit=0.0,
        credit=99000.0, balance=100000.0
    )
    tn_even_later = Transaction(
        asset=asset,
        quantity=100,
        dt=even_later_dt,
        price=567.0,
        order_id=1,
        commission=15.78
    )
    port.transact_asset(tn_even_later)

    assert port.cash == 43284.22
    assert port.total_market_value == 56700.00
    assert port.total_equity == 99984.22

    description = "LONG 100 EQ:AAA 567.00 07/10/2017"
    pe_tn = PortfolioEvent(
        dt=even_later_dt, type="asset_transaction",
        description=description, debit=56715.78,
        credit=0.0, balance=43284.22
    )

    assert port.history == [pe_sub1, pe_sub2, pe_tn]
    assert port.current_dt == even_later_dt


def test_portfolio_to_dict_empty_portfolio():
    """
    Test 'portfolio_to_dict' method for an empty Portfolio.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    port = Portfolio(start_dt)
    port.subscribe_funds(start_dt, 100000.0)
    port_dict = port.portfolio_to_dict()
    assert port_dict == {}


def test_portfolio_to_dict_for_two_holdings():
    """
    Test portfolio_to_dict for two holdings.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    asset1_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
    asset2_dt = pd.Timestamp('2017-10-07 08:00:00', tz=pytz.UTC)
    update_dt = pd.Timestamp('2017-10-08 08:00:00', tz=pytz.UTC)
    asset1 = 'EQ:AAA'
    asset2 = 'EQ:BBB'

    port = Portfolio(start_dt, portfolio_id='1234')
    port.subscribe_funds(start_dt, 100000.0)
    tn_asset1 = Transaction(
        asset=asset1, quantity=100, dt=asset1_dt,
        price=567.0, order_id=1, commission=15.78
    )
    port.transact_asset(tn_asset1)

    tn_asset2 = Transaction(
        asset=asset2, quantity=100, dt=asset2_dt,
        price=123.0, order_id=2, commission=7.64
    )
    port.transact_asset(tn_asset2)
    port.update_market_value_of_asset(asset2, 134.0, update_dt)
    test_holdings = {
        asset1: {
            "quantity": 100,
            "market_value": 56700.0,
            "unrealised_pnl": -15.78,
            "realised_pnl": 0.0,
            "total_pnl": -15.78
        },
        asset2: {
            "quantity": 100,
            "market_value": 13400.0,
            "unrealised_pnl": 1092.3600000000006,
            "realised_pnl": 0.0,
            "total_pnl": 1092.3600000000006
        }
    }
    port_holdings = port.portfolio_to_dict()

    # This is needed because we're not using Decimal
    # datatypes and have to compare slightly differing
    # floating point representations
    for asset in (asset1, asset2):
        for key, val in test_holdings[asset].items():
            assert port_holdings[asset][key] == pytest.approx(
                test_holdings[asset][key]
            )


def test_update_market_value_of_asset_not_in_list():
    """
    Test update_market_value_of_asset for asset not in list.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    later_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
    port = Portfolio(start_dt)
    asset = 'EQ:AAA'
    update = port.update_market_value_of_asset(
        asset, 54.34, later_dt
    )
    assert update is None


def test_update_market_value_of_asset_negative_price():
    """
    Test update_market_value_of_asset for
    asset with negative price.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    later_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
    port = Portfolio(start_dt)

    asset = 'EQ:AAA'
    port.subscribe_funds(later_dt, 100000.0)
    tn_asset = Transaction(
        asset=asset,
        quantity=100,
        dt=later_dt,
        price=567.0,
        order_id=1,
        commission=15.78
    )
    port.transact_asset(tn_asset)
    with pytest.raises(ValueError):
        port.update_market_value_of_asset(
            asset, -54.34, later_dt
        )


def test_update_market_value_of_asset_earlier_date():
    """
    Test update_market_value_of_asset for asset
    with current_trade_date in past
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    earlier_dt = pd.Timestamp('2017-10-04 08:00:00', tz=pytz.UTC)
    later_dt = pd.Timestamp('2017-10-06 08:00:00', tz=pytz.UTC)
    port = Portfolio(start_dt, portfolio_id='1234')

    asset = 'EQ:AAA'
    port.subscribe_funds(later_dt, 100000.0)
    tn_asset = Transaction(
        asset=asset,
        quantity=100,
        dt=later_dt,
        price=567.0,
        order_id=1,
        commission=15.78
    )
    port.transact_asset(tn_asset)
    with pytest.raises(ValueError):
        port.update_market_value_of_asset(
            asset, 50.23, earlier_dt
        )


def test_history_to_df_empty():
    """
    Test 'history_to_df' with no events.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    port = Portfolio(start_dt)
    hist_df = port.history_to_df()
    test_df = pd.DataFrame(
        [], columns=[
            "date", "type", "description",
            "debit", "credit", "balance"
        ]
    )
    test_df.set_index(keys=["date"], inplace=True)
    assert sorted(test_df.columns) == sorted(hist_df.columns)
    assert len(test_df) == len(hist_df)
    assert len(hist_df) == 0
