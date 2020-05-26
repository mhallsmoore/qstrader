from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest
import pytz

from qstrader.signals.momentum import MomentumSignal


@pytest.mark.parametrize(
    'start_dt,lookbacks,prices,expected',
    [
        (
            pd.Timestamp('2019-01-01 14:30:00', tz=pytz.utc),
            [6, 12],
            [
                99.34, 101.87, 98.32, 92.98, 103.87,
                104.51, 97.62, 95.22, 96.09, 100.34,
                105.14, 107.49, 90.23, 89.43, 87.68
            ],
            [-0.08752211468415028, -0.10821806346623242]
        )
    ]
)
def test_momentum_signal(start_dt, lookbacks, prices, expected):
    """
    Checks that the momentum signal correctly calculates the
    holding period return based momentum for various lookbacks.
    """
    universe = Mock()
    universe.get_assets.return_value = ['EQ:SPY']

    mom = MomentumSignal(start_dt, universe, lookbacks)
    for price_idx in range(len(prices)):
        mom.append('EQ:SPY', prices[price_idx])

    for i, lookback in enumerate(lookbacks):
        assert np.isclose(mom('EQ:SPY', lookback), expected[i])
