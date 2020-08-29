from unittest.mock import Mock

import pandas as pd
import pytest
import pytz


from qstrader.portcon.order_sizer.dollar_weighted import (
    DollarWeightedCashBufferedOrderSizer
)


@pytest.mark.parametrize(
    "cash_buffer_perc,expected",
    [
        (-1.0, None),
        (0.0, 0.0),
        (0.5, 0.5),
        (0.99, 0.99),
        (1.0, 1.0),
        (1.5, None)
    ]
)
def test_check_set_cash_buffer(cash_buffer_perc, expected):
    """
    Checks that the cash buffer falls into the appropriate
    range and raises otherwise.
    """
    broker = Mock()
    broker_portfolio_id = "1234"
    data_handler = Mock()

    if expected is None:
        with pytest.raises(ValueError):
            order_sizer = DollarWeightedCashBufferedOrderSizer(
                broker, broker_portfolio_id, data_handler, cash_buffer_perc
            )
    else:
        order_sizer = DollarWeightedCashBufferedOrderSizer(
            broker, broker_portfolio_id, data_handler, cash_buffer_perc
        )
        assert order_sizer.cash_buffer_percentage == cash_buffer_perc


@pytest.mark.parametrize(
    "weights,expected",
    [
        (
            {'EQ:ABC': 0.2, 'EQ:DEF': 0.6},
            {'EQ:ABC': 0.25, 'EQ:DEF': 0.75}
        ),
        (
            {'EQ:ABC': 0.5, 'EQ:DEF': 0.5},
            {'EQ:ABC': 0.5, 'EQ:DEF': 0.5}
        ),
        (
            {'EQ:ABC': 0.01, 'EQ:DEF': 0.01},
            {'EQ:ABC': 0.5, 'EQ:DEF': 0.5}
        ),
        (
            {'EQ:ABC': 0.1, 'EQ:DEF': 0.3, 'EQ:GHI': 0.02, 'EQ:JKL': 0.8},
            {'EQ:ABC': 0.1 / 1.22, 'EQ:DEF': 0.3 / 1.22, 'EQ:GHI': 0.02 / 1.22, 'EQ:JKL': 0.8 / 1.22},
        ),
        (
            {'EQ:ABC': 0.0, 'EQ:DEF': 0.0},
            {'EQ:ABC': 0.0, 'EQ:DEF': 0.0}
        ),
        (
            {'EQ:ABC': -0.2, 'EQ:DEF': 0.6},
            None
        ),
    ]
)
def test_normalise_weights(weights, expected):
    """
    Checks that the _normalise_weights method rescales the weights
    to ensure that they sum to unity.
    """
    broker = Mock()
    broker_portfolio_id = "1234"
    data_handler = Mock()
    cash_buffer_perc = 0.05

    order_sizer = DollarWeightedCashBufferedOrderSizer(
        broker, broker_portfolio_id, data_handler, cash_buffer_perc
    )
    if expected is None:
        with pytest.raises(ValueError):
            result = order_sizer._normalise_weights(weights)
    else:
        result = order_sizer._normalise_weights(weights)
        assert result == pytest.approx(expected)


@pytest.mark.parametrize(
    "total_equity,cash_buffer_perc,weights,asset_prices,expected",
    [
        (
            1e6,
            0.05,
            {'EQ:SPY': 0.5, 'EQ:AGG': 0.5},
            {'EQ:SPY': 250.0, 'EQ:AGG': 150.0},
            {'EQ:SPY': {'quantity': 1900}, 'EQ:AGG': {'quantity': 3166}}
        ),
        (
            325000.0,
            0.15,
            {'EQ:SPY': 0.6, 'EQ:AGG': 0.4},
            {'EQ:SPY': 352.0, 'EQ:AGG': 178.0},
            {'EQ:SPY': {'quantity': 470}, 'EQ:AGG': {'quantity': 620}}
        ),
        (
            687523.0,
            0.025,
            {'EQ:SPY': 0.05, 'EQ:AGG': 0.328, 'EQ:TLT': 0.842, 'EQ:GLD': 0.9113},
            {'EQ:SPY': 1036.23, 'EQ:AGG': 456.55, 'EQ:TLT': 987.63, 'EQ:GLD': 14.76},
            {
                'EQ:SPY': {'quantity': 15},
                'EQ:AGG': {'quantity': 225},
                'EQ:TLT': {'quantity': 268},
                'EQ:GLD': {'quantity': 19418},
            }
        )
    ]
)
def test_call(total_equity, cash_buffer_perc, weights, asset_prices, expected):
    """
    Checks that the __call__ method correctly outputs the target
    portfolio from a given set of weights and a timestamp.
    """
    dt = pd.Timestamp('2019-01-01 15:00:00', tz=pytz.utc)
    broker_portfolio_id = "1234"

    broker = Mock()
    broker.get_portfolio_total_equity.return_value = total_equity
    broker.fee_model.calc_total_cost.return_value = 0.0

    data_handler = Mock()
    data_handler.get_asset_latest_ask_price.side_effect = lambda self, x: asset_prices[x]

    order_sizer = DollarWeightedCashBufferedOrderSizer(
        broker, broker_portfolio_id, data_handler, cash_buffer_perc
    )

    result = order_sizer(dt, weights)
    assert result == expected
