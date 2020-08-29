from unittest.mock import Mock

import pandas as pd
import pytest
import pytz

from qstrader.execution.order import Order
from qstrader.portcon.pcm import PortfolioConstructionModel


SENTINEL_DT = pd.Timestamp('2019-01-01 15:00:00', tz=pytz.utc)


@pytest.mark.parametrize(
    'description,port_dict,uni_assets,expected',
    [
        (
            'empty on both sides',
            {}, [], []
        ),
        (
            'partially intersecting set of assets',
            {
                'EQ:ABC': 100,
                'EQ:DEF': 250,
                'EQ:GHI': 38
            },
            ['EQ:123', 'EQ:GHI', 'EQ:ABC', 'EQ:567'],
            ['EQ:123', 'EQ:567', 'EQ:ABC', 'EQ:DEF', 'EQ:GHI']
        ),
        (
            'non-intersecting set of assets',
            {'EQ:ABC': 450, 'EQ:DEF': 210},
            ['EQ:567', 'EQ:123'],
            ['EQ:123', 'EQ:567', 'EQ:ABC', 'EQ:DEF']
        )
    ]
)
def test_obtain_full_asset_list(description, port_dict, uni_assets, expected):
    """
    Tests the _obtain_full_asset_list method of the
    PortfolioConstructionModel base class.
    """
    port_id = '1234'

    broker = Mock()
    broker.get_portfolio_as_dict.return_value = port_dict

    universe = Mock()
    universe.get_assets.return_value = uni_assets

    order_sizer = Mock()
    optimiser = Mock()

    pcm = PortfolioConstructionModel(
        broker, port_id, universe, order_sizer, optimiser
    )

    result = pcm._obtain_full_asset_list(SENTINEL_DT)
    assert result == expected


@pytest.mark.parametrize(
    'description,full_assets,expected',
    [
        (
            'empty assets',
            [],
            {}
        ),
        (
            'non-empty assets',
            ['EQ:ABC', 'EQ:123', 'EQ:A1B2'],
            {'EQ:ABC': 0.0, 'EQ:123': 0.0, 'EQ:A1B2': 0.0}
        )
    ]
)
def test_create_zero_target_weight_vector(description, full_assets, expected):
    """
    Tests the _create_zero_target_weight_vector method of the
    PortfolioConstructionModel base class.
    """
    port_id = '1234'

    broker = Mock()
    universe = Mock()
    order_sizer = Mock()
    optimiser = Mock()

    pcm = PortfolioConstructionModel(
        broker, port_id, universe, order_sizer, optimiser
    )

    result = pcm._create_zero_target_weight_vector(full_assets)
    assert result == expected


@pytest.mark.parametrize(
    'description,zero_weights,optimised_weights,expected',
    [
        (
            'empty weights on both sides',
            {},
            {},
            {}
        ),
        (
            'non-intersecting weights',
            {'EQ:ABC': 0.0, 'EQ:DEF': 0.0},
            {'EQ:123': 0.5, 'EQ:567': 0.5},
            {'EQ:ABC': 0.0, 'EQ:DEF': 0.0, 'EQ:123': 0.5, 'EQ:567': 0.5},
        ),
        (
            'partially-intersecting weights',
            {'EQ:ABC': 0.0, 'EQ:DEF': 0.0, 'EQ:123': 0.0},
            {'EQ:123': 0.25, 'EQ:567': 0.25, 'EQ:890': 0.5},
            {'EQ:ABC': 0.0, 'EQ:DEF': 0.0, 'EQ:123': 0.25, 'EQ:567': 0.25, 'EQ:890': 0.5},
        ),
        (
            'fully-intersecting weights',
            {'EQ:ABC': 0.0, 'EQ:DEF': 0.0, 'EQ:123': 0.0},
            {'EQ:ABC': 0.25, 'EQ:DEF': 0.25, 'EQ:123': 0.5},
            {'EQ:ABC': 0.25, 'EQ:DEF': 0.25, 'EQ:123': 0.5},
        )
    ]
)
def test_create_full_asset_weight_vector(
    description, zero_weights, optimised_weights, expected
):
    """
    Tests the _create_full_asset_weight_vector method of the
    PortfolioConstructionModel base class.
    """
    port_id = '1234'

    broker = Mock()
    universe = Mock()
    order_sizer = Mock()
    optimiser = Mock()

    pcm = PortfolioConstructionModel(
        broker, port_id, universe, order_sizer, optimiser
    )

    result = pcm._create_full_asset_weight_vector(zero_weights, optimised_weights)
    assert result == expected


@pytest.mark.parametrize(
    'description,target_portfolio,current_portfolio,expected',
    [
        (
            'empty portfolios on both sides',
            {},
            {},
            []
        ),
        (
            'non-empty equal portfolios on both sides - no orders',
            {'EQ:ABC': {'quantity': 100}, 'EQ:DEF': {'quantity': 250}},
            {'EQ:ABC': {'quantity': 100}, 'EQ:DEF': {'quantity': 250}},
            []
        ),
        (
            'non-empty target portfolio with empty current portfolio',
            {'EQ:ABC': {'quantity': 100}, 'EQ:DEF': {'quantity': 250}},
            {},
            [
                Order(SENTINEL_DT, 'EQ:ABC', 100),
                Order(SENTINEL_DT, 'EQ:DEF', 250)
            ]
        ),
        (
            'empty target portfolio with non-empty current portfolio',
            {},
            {'EQ:ABC': {'quantity': 345}, 'EQ:DEF': {'quantity': 223}},
            [
                Order(SENTINEL_DT, 'EQ:ABC', -345),
                Order(SENTINEL_DT, 'EQ:DEF', -250)
            ]
        ),
        (
            'non-empty portfolios, non-intersecting symbols',
            {'EQ:ABC': {'quantity': 123}, 'EQ:DEF': {'quantity': 456}},
            {'EQ:GHI': {'quantity': 217}, 'EQ:JKL': {'quantity': 48}},
            [
                Order(SENTINEL_DT, 'EQ:ABC', 123),
                Order(SENTINEL_DT, 'EQ:DEF', 456),
                Order(SENTINEL_DT, 'EQ:GHI', -217),
                Order(SENTINEL_DT, 'EQ:JKL', -48)
            ]
        ),
        (
            'non-empty portfolios, partially-intersecting symbols',
            {'EQ:ABC': {'quantity': 123}, 'EQ:DEF': {'quantity': 456}},
            {'EQ:DEF': {'quantity': 217}, 'EQ:GHI': {'quantity': 48}},
            [
                Order(SENTINEL_DT, 'EQ:ABC', 123),
                Order(SENTINEL_DT, 'EQ:DEF', 239),
                Order(SENTINEL_DT, 'EQ:GHI', -48)
            ]
        ),
        (
            'non-empty portfolios, fully-intersecting symbols',
            {'EQ:ABC': {'quantity': 123}, 'EQ:DEF': {'quantity': 456}},
            {'EQ:ABC': {'quantity': 217}, 'EQ:DEF': {'quantity': 48}},
            [
                Order(SENTINEL_DT, 'EQ:ABC', -94),
                Order(SENTINEL_DT, 'EQ:DEF', 408)
            ]
        )
    ]
)
def test_generate_rebalance_orders(
    helpers, description, target_portfolio, current_portfolio, expected
):
    """
    Tests the _generate_rebalance_orders method of the
    PortfolioConstructionModel base class.
    """
    port_id = '1234'

    broker = Mock()
    universe = Mock()
    order_sizer = Mock()
    optimiser = Mock()

    pcm = PortfolioConstructionModel(
        broker, port_id, universe, order_sizer, optimiser
    )

    result = pcm._generate_rebalance_orders(SENTINEL_DT, target_portfolio, current_portfolio)
    helpers.assert_order_lists_equal(result, expected)
