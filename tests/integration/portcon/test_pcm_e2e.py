from unittest.mock import Mock

import pandas as pd
import pytz

from qstrader.alpha_model.fixed_signals import FixedSignalsAlphaModel
from qstrader.asset.universe.static import StaticUniverse
from qstrader.broker.simulated_broker import SimulatedBroker
from qstrader.exchange.simulated_exchange import SimulatedExchange
from qstrader.execution.order import Order
from qstrader.portcon.pcm import PortfolioConstructionModel
from qstrader.portcon.optimiser.fixed_weight import (
    FixedWeightPortfolioOptimiser
)
from qstrader.portcon.order_sizer.dollar_weighted import (
    DollarWeightedCashBufferedOrderSizer
)


def test_pcm_fixed_weight_optimiser_fixed_alpha_weights_call_end_to_end(
    helpers
):
    """
    Tests the full portfolio base class logic for carrying out
    rebalancing.

    TODO: DataHandler is mocked. A non-disk based data source
    should be utilised instead.
    """
    first_dt = pd.Timestamp('2019-01-01 15:00:00', tz=pytz.utc)
    asset_list = ['EQ:SPY', 'EQ:AGG', 'EQ:TLT', 'EQ:GLD']
    initial_funds = 1e6
    account_id = '1234'
    port_id = '1234'
    cash_buffer_perc = 0.05

    exchange = SimulatedExchange(first_dt)
    universe = StaticUniverse(asset_list)

    mock_asset_prices_first = {
        'EQ:SPY': 56.87,
        'EQ:AGG': 219.45,
        'EQ:TLT': 178.33,
        'EQ:GLD': 534.21
    }
    data_handler = Mock()
    data_handler.get_asset_latest_ask_price.side_effect = \
        lambda self, x: mock_asset_prices_first[x]

    broker = SimulatedBroker(
        first_dt, exchange, data_handler, account_id,
        initial_funds=initial_funds
    )
    broker.create_portfolio(port_id, 'Portfolio')
    broker.subscribe_funds_to_portfolio(port_id, initial_funds)

    order_sizer = DollarWeightedCashBufferedOrderSizer(
        broker, port_id, data_handler, cash_buffer_perc
    )
    optimiser = FixedWeightPortfolioOptimiser(data_handler)

    alpha_weights = {
        'EQ:SPY': 0.345,
        'EQ:AGG': 0.611,
        'EQ:TLT': 0.870,
        'EQ:GLD': 0.0765
    }
    alpha_model = FixedSignalsAlphaModel(alpha_weights)

    pcm = PortfolioConstructionModel(
        broker, port_id, universe, order_sizer, optimiser, alpha_model
    )

    result_first = pcm(first_dt)
    expected_first = [
        Order(first_dt, 'EQ:AGG', 1390),
        Order(first_dt, 'EQ:GLD', 71),
        Order(first_dt, 'EQ:SPY', 3029),
        Order(first_dt, 'EQ:TLT', 2436)
    ]
    helpers.assert_order_lists_equal(result_first, expected_first)
