from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest
import pytz

from qstrader.signals.sma import SMASignal


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
            [96.71833333333333, 97.55]
        )
    ]
)
def test_sma_signal(start_dt, lookbacks, prices, expected):
    """
    Checks that the SMA signal correctly calculates the
    simple moving average for various lookbacks.
    """
    universe = Mock()
    universe.get_assets.return_value = ['EQ:SPY']

    sma = SMASignal(start_dt, universe, lookbacks)
    for price_idx in range(len(prices)):
        sma.append('EQ:SPY', prices[price_idx])

    for i, lookback in enumerate(lookbacks):
        assert np.isclose(sma('EQ:SPY', lookback), expected[i])
