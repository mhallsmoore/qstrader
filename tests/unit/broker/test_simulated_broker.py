import queue

import numpy as np
import pandas as pd
import pytest
import pytz

from qstrader.broker.portfolio.portfolio import Portfolio
from qstrader.broker.simulated_broker import SimulatedBroker
from qstrader.broker.fee_model.zero_fee_model import ZeroFeeModel
from qstrader import settings


class ExchangeMock(object):
    def get_latest_asset_bid_ask(self, asset):
        return (np.NaN, np.NaN)

    def is_open_at_datetime(self, dt):
        return True


class ExchangeMockException(object):
    def get_latest_asset_bid_ask(self, asset):
        raise ValueError("No price available!")

    def is_open_at_datetime(self, dt):
        return True


class ExchangeMockPrice(object):
    def is_open_at_datetime(self, dt):
        return True


class DataHandlerMock(object):
    def get_asset_latest_bid_ask_price(self, dt, asset):
        return (np.NaN, np.NaN)

    def get_asset_latest_mid_price(self, dt, asset):
        return np.NaN


class DataHandlerMockPrice(object):
    def get_asset_latest_bid_ask_price(self, dt, asset):
        return (53.45, 53.47)

    def get_asset_latest_mid_price(self, dt, asset):
        return (53.47 - 53.45) / 2.0


class OrderMock(object):
    def __init__(self, asset, quantity, order_id=None):
        self.asset = asset
        self.quantity = quantity
        self.order_id = 1 if order_id is None else order_id
        self.direction = np.copysign(1, self.quantity)


class AssetMock(object):
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol


def test_initial_settings_for_default_simulated_broker():
    """
    Tests that the SimulatedBroker settings are set
    correctly for default settings.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    # Test a default SimulatedBroker
    sb1 = SimulatedBroker(start_dt, exchange, data_handler)

    assert sb1.start_dt == start_dt
    assert sb1.current_dt == start_dt
    assert sb1.exchange == exchange
    assert sb1.account_id is None
    assert sb1.base_currency == "USD"
    assert sb1.initial_funds == 0.0
    assert type(sb1.fee_model) == ZeroFeeModel

    tcb1 = dict(
        zip(
            settings.SUPPORTED['CURRENCIES'],
            [0.0] * len(settings.SUPPORTED['CURRENCIES'])
        )
    )

    assert sb1.cash_balances == tcb1
    assert sb1.portfolios == {}
    assert sb1.open_orders == {}

    # Test a SimulatedBroker with some parameters set
    sb2 = SimulatedBroker(
        start_dt, exchange, data_handler, account_id="ACCT1234",
        base_currency="GBP", initial_funds=1e6,
        fee_model=ZeroFeeModel()
    )

    assert sb2.start_dt == start_dt
    assert sb2.current_dt == start_dt
    assert sb2.exchange == exchange
    assert sb2.account_id == "ACCT1234"
    assert sb2.base_currency == "GBP"
    assert sb2.initial_funds == 1e6
    assert type(sb2.fee_model) == ZeroFeeModel

    tcb2 = dict(
        zip(
            settings.SUPPORTED['CURRENCIES'],
            [0.0] * len(settings.SUPPORTED['CURRENCIES'])
        )
    )
    tcb2["GBP"] = 1e6

    assert sb2.cash_balances == tcb2
    assert sb2.portfolios == {}
    assert sb2.open_orders == {}


def test_bad_set_base_currency():
    """
    Checks _set_base_currency raises ValueError
    if a non-supported currency is attempted to be
    set as the base currency.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    with pytest.raises(ValueError):
        SimulatedBroker(
            start_dt, exchange, data_handler, base_currency="XYZ"
        )


def test_good_set_base_currency():
    """
    Checks _set_base_currency sets the currency
    correctly if it is supported by QSTrader.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(
        start_dt, exchange, data_handler, base_currency="EUR"
    )
    assert sb.base_currency == "EUR"


def test_bad_set_initial_funds():
    """
    Checks _set_initial_funds raises ValueError
    if initial funds amount is negative.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    with pytest.raises(ValueError):
        SimulatedBroker(
            start_dt, exchange, data_handler, initial_funds=-56.34
        )


def test_good_set_initial_funds():
    """
    Checks _set_initial_funds sets the initial funds
    correctly if it is a positive floating point value.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler, initial_funds=1e4)
    assert sb._set_initial_funds(1e4) == 1e4


def test_all_cases_of_set_broker_commission():
    """
    Tests that _set_broker_commission correctly sets the
    appropriate broker commission model depending upon
    user choice.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    # Broker commission is None
    sb1 = SimulatedBroker(start_dt, exchange, data_handler)
    assert sb1.fee_model.__class__.__name__ == "ZeroFeeModel"

    # Broker commission is specified as a subclass
    # of FeeModel abstract base class
    bc2 = ZeroFeeModel()
    sb2 = SimulatedBroker(
        start_dt, exchange, data_handler, fee_model=bc2
    )
    assert sb2.fee_model.__class__.__name__ == "ZeroFeeModel"

    # FeeModel is mis-specified and thus
    # raises a TypeError
    with pytest.raises(TypeError):
        SimulatedBroker(
            start_dt, exchange, data_handler, fee_model="bad_fee_model"
        )


def test_set_cash_balances():
    """
    Checks _set_cash_balances for zero and non-zero
    initial_funds.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    # Zero initial funds
    sb1 = SimulatedBroker(
        start_dt, exchange, data_handler, initial_funds=0.0
    )
    tcb1 = dict(
        zip(
            settings.SUPPORTED['CURRENCIES'],
            [0.0] * len(settings.SUPPORTED['CURRENCIES'])
        )
    )
    assert sb1._set_cash_balances() == tcb1

    # Non-zero initial funds
    sb2 = SimulatedBroker(
        start_dt, exchange, data_handler, initial_funds=12345.0
    )
    tcb2 = dict(
        zip(
            settings.SUPPORTED['CURRENCIES'],
            [0.0] * len(settings.SUPPORTED['CURRENCIES'])
        )
    )
    tcb2["USD"] = 12345.0
    assert sb2._set_cash_balances() == tcb2


def test_set_initial_portfolios():
    """
    Check _set_initial_portfolios method for return
    of an empty dictionary.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)
    assert sb._set_initial_portfolios() == {}


def test_set_initial_open_orders():
    """
    Check _set_initial_open_orders method for return
    of an empty dictionary.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)
    assert sb._set_initial_open_orders() == {}


def test_subscribe_funds_to_account():
    """
    Tests subscribe_funds_to_account method for:
    * Raising ValueError with negative amount
    * Correctly setting cash_balances for a positive amount
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # Raising ValueError with negative amount
    with pytest.raises(ValueError):
        sb.subscribe_funds_to_account(-4306.23)

    # Correctly setting cash_balances for a positive amount
    sb.subscribe_funds_to_account(165303.23)
    assert sb.cash_balances[sb.base_currency] == 165303.23


def test_withdraw_funds_from_account():
    """
    Tests withdraw_funds_from_account method for:
    * Raising ValueError with negative amount
    * Raising ValueError for lack of cash
    * Correctly setting cash_balances for positive amount
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler, initial_funds=1e6)

    # Raising ValueError with negative amount
    with pytest.raises(ValueError):
        sb.withdraw_funds_from_account(-4306.23)

    # Raising ValueError for lack of cash
    with pytest.raises(ValueError):
        sb.withdraw_funds_from_account(2e6)

    # Correctly setting cash_balances for a positive amount
    sb.withdraw_funds_from_account(3e5)
    assert sb.cash_balances[sb.base_currency] == 7e5


def test_get_account_cash_balance():
    """
    Tests get_account_cash_balance method for:
    * If currency is None, return the cash_balances
    * If the currency code isn't in the cash_balances
    dictionary, then raise ValueError
    * Otherwise, return the appropriate cash balance
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(
        start_dt, exchange, data_handler, initial_funds=1000.0
    )

    # If currency is None, return the cash balances
    sbcb1 = sb.get_account_cash_balance()
    tcb1 = dict(
        zip(
            settings.SUPPORTED['CURRENCIES'],
            [0.0] * len(settings.SUPPORTED['CURRENCIES'])
        )
    )
    tcb1["USD"] = 1000.0
    assert sbcb1 == tcb1

    # If the currency code isn't in the cash_balances
    # dictionary, then raise ValueError
    with pytest.raises(ValueError):
        sb.get_account_cash_balance(currency="XYZ")

    # Otherwise, return appropriate cash balance
    assert sb.get_account_cash_balance(currency="USD") == 1000.0
    assert sb.get_account_cash_balance(currency="EUR") == 0.0


def test_get_account_total_market_value():
    """
    Tests get_account_total_market_value method for:
    * The correct market values after cash is subscribed.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # Subscribe all necessary funds and create portfolios
    sb.subscribe_funds_to_account(300000.0)
    sb.create_portfolio(portfolio_id="1", name="My Portfolio #1")
    sb.create_portfolio(portfolio_id="2", name="My Portfolio #1")
    sb.create_portfolio(portfolio_id="3", name="My Portfolio #1")
    sb.subscribe_funds_to_portfolio("1", 100000.0)
    sb.subscribe_funds_to_portfolio("2", 100000.0)
    sb.subscribe_funds_to_portfolio("3", 100000.0)

    # Check that the market value is correct
    res_equity = sb.get_account_total_equity()
    test_equity = {
        "1": 100000.0,
        "2": 100000.0,
        "3": 100000.0,
        "master": 300000.0
    }
    assert res_equity == test_equity


def test_create_portfolio():
    """
    Tests create_portfolio method for:
    * If portfolio_id already in the dictionary keys,
    raise ValueError
    * If it isn't, check that they portfolio and open
    orders dictionary was created correctly.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # If portfolio_id isn't in the dictionary, then check it
    # was created correctly, along with the orders dictionary
    sb.create_portfolio(portfolio_id=1234, name="My Portfolio")
    assert "1234" in sb.portfolios
    assert isinstance(sb.portfolios["1234"], Portfolio)
    assert "1234" in sb.open_orders
    assert isinstance(sb.open_orders["1234"], queue.Queue)

    # If portfolio is already in the dictionary
    # then raise ValueError
    with pytest.raises(ValueError):
        sb.create_portfolio(
            portfolio_id=1234, name="My Portfolio"
        )


def test_list_all_portfolio():
    """
    Tests list_all_portfolios method for:
    * If empty portfolio dictionary, return empty list
    * If non-empty, return sorted list via the portfolio IDs
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # If empty portfolio dictionary, return empty list
    assert sb.list_all_portfolios() == []

    # If non-empty, return sorted list via the portfolio IDs
    sb.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    sb.create_portfolio(portfolio_id="z154", name="My Portfolio #2")
    sb.create_portfolio(portfolio_id="abcd", name="My Portfolio #3")

    res_ports = sorted([
        p.portfolio_id
        for p in sb.list_all_portfolios()
    ])
    test_ports = ["1234", "abcd", "z154"]
    assert res_ports == test_ports


def test_subscribe_funds_to_portfolio():
    """
    Tests subscribe_funds_to_portfolio method for:
    * Raising ValueError with negative amount
    * Raising ValueError if portfolio does not exist
    * Correctly setting cash_balances for a positive amount
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # Raising ValueError with negative amount
    with pytest.raises(ValueError):
        sb.subscribe_funds_to_portfolio("1234", -4306.23)

    # Raising KeyError if portfolio doesn't exist
    with pytest.raises(KeyError):
        sb.subscribe_funds_to_portfolio("1234", 5432.12)

    # Add in cash balance to the account
    sb.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    sb.subscribe_funds_to_account(165303.23)

    # Raising ValueError if not enough cash
    with pytest.raises(ValueError):
        sb.subscribe_funds_to_portfolio("1234", 200000.00)

    # If everything else worked, check balances are correct
    sb.subscribe_funds_to_portfolio("1234", 100000.00)
    assert sb.cash_balances[sb.base_currency] == 65303.23000000001
    assert sb.portfolios["1234"].cash == 100000.00


def test_withdraw_funds_from_portfolio():
    """
    Tests withdraw_funds_from_portfolio method for:
    * Raising ValueError with negative amount
    * Raising ValueError if portfolio does not exist
    * Raising ValueError for a lack of cash
    * Correctly setting cash_balances for a positive amount
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # Raising ValueError with negative amount
    with pytest.raises(ValueError):
        sb.withdraw_funds_from_portfolio("1234", -4306.23)

    # Raising KeyError if portfolio doesn't exist
    with pytest.raises(KeyError):
        sb.withdraw_funds_from_portfolio("1234", 5432.12)

    # Add in cash balance to the account
    sb.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    sb.subscribe_funds_to_account(165303.23)
    sb.subscribe_funds_to_portfolio("1234", 100000.00)

    # Raising ValueError if not enough cash
    with pytest.raises(ValueError):
        sb.withdraw_funds_from_portfolio("1234", 200000.00)

    # If everything else worked, check balances are correct
    sb.withdraw_funds_from_portfolio("1234", 50000.00)
    assert sb.cash_balances[sb.base_currency] == 115303.23000000001
    assert sb.portfolios["1234"].cash == 50000.00


def test_get_portfolio_cash_balance():
    """
    Tests get_portfolio_cash_balance method for:
    * Raising ValueError if portfolio_id not in keys
    * Correctly obtaining the value after cash transfers
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # Raising ValueError if portfolio_id not in keys
    with pytest.raises(ValueError):
        sb.get_portfolio_cash_balance("5678")

    # Create fund transfers and portfolio
    sb.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    sb.subscribe_funds_to_account(175000.0)
    sb.subscribe_funds_to_portfolio("1234", 100000.00)

    # Check correct values obtained after cash transfers
    assert sb.get_portfolio_cash_balance("1234") == 100000.0


def test_get_portfolio_total_market_value():
    """
    Tests get_portfolio_total_market_value method for:
    * Raising ValueError if portfolio_id not in keys
    * Correctly obtaining the market value after cash transfers
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # Raising KeyError if portfolio_id not in keys
    with pytest.raises(KeyError):
        sb.get_portfolio_total_market_value("5678")

    # Create fund transfers and portfolio
    sb.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    sb.subscribe_funds_to_account(175000.0)
    sb.subscribe_funds_to_portfolio("1234", 100000.00)

    # Check correct values obtained after cash transfers
    assert sb.get_portfolio_total_equity("1234") == 100000.0


def test_submit_order():
    """
    Tests the execute_order method for:
    * Raises ValueError if no portfolio_id
    * Raises ValueError if bid/ask is (np.NaN, np.NaN)
    * Checks that bid/ask are correctly set dependent
    upon order direction
    * Checks that portfolio values are correct after
    carrying out a transaction
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)

    # Raising KeyError if portfolio_id not in keys
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)
    asset = 'EQ:RDSB'
    quantity = 100
    order = OrderMock(asset, quantity)
    with pytest.raises(KeyError):
        sb.submit_order("1234", order)

    # Raises ValueError if bid/ask is (np.NaN, np.NaN)
    exchange_exception = ExchangeMockException()
    sbnp = SimulatedBroker(start_dt, exchange_exception, data_handler)
    sbnp.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    quantity = 100
    order = OrderMock(asset, quantity)
    with pytest.raises(ValueError):
        sbnp._execute_order(start_dt, "1234", order)

    # Checks that bid/ask are correctly set dependent on
    # order direction

    # Positive direction
    exchange_price = ExchangeMockPrice()
    data_handler_price = DataHandlerMockPrice()

    sbwp = SimulatedBroker(start_dt, exchange_price, data_handler_price)
    sbwp.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    sbwp.subscribe_funds_to_account(175000.0)
    sbwp.subscribe_funds_to_portfolio("1234", 100000.00)
    quantity = 1000
    order = OrderMock(asset, quantity)
    sbwp.submit_order("1234", order)
    sbwp.update(start_dt)

    port = sbwp.portfolios["1234"]
    assert port.cash == 46530.0
    assert port.total_market_value == 53470.0
    assert port.total_equity == 100000.0
    assert port.pos_handler.positions[asset].unrealised_pnl == 0.0
    assert port.pos_handler.positions[asset].market_value == 53470.0
    assert port.pos_handler.positions[asset].net_quantity == 1000

    # Negative direction
    exchange_price = ExchangeMockPrice()
    sbwp = SimulatedBroker(start_dt, exchange_price, data_handler_price)
    sbwp.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    sbwp.subscribe_funds_to_account(175000.0)
    sbwp.subscribe_funds_to_portfolio("1234", 100000.00)
    quantity = -1000
    order = OrderMock(asset, quantity)
    sbwp.submit_order("1234", order)
    sbwp.update(start_dt)

    port = sbwp.portfolios["1234"]
    assert port.cash == 153450.0
    assert port.total_market_value == -53450.0
    assert port.total_equity == 100000.0
    assert port.pos_handler.positions[asset].unrealised_pnl == 0.0
    assert port.pos_handler.positions[asset].market_value == -53450.0
    assert port.pos_handler.positions[asset].net_quantity == -1000


def test_update_sets_correct_time():
    """
    Tests that the update method sets the current
    time correctly.
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    new_dt = pd.Timestamp('2017-10-07 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)
    sb.update(new_dt)
    assert sb.current_dt == new_dt
