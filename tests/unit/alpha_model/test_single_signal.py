from unittest.mock import Mock

import pandas as pd
import pytest
import pytz

from qstrader.alpha_model.single_signal import SingleSignalAlphaModel


@pytest.mark.parametrize(
    'signal,expected_signals',
    [
        (0.75, {'EQ:SPY': 0.75, 'EQ:AGG': 0.75, 'EQ:GLD': 0.75}),
        (-0.25, {'EQ:SPY': -0.25, 'EQ:AGG': -0.25, 'EQ:GLD': -0.25})
    ]
)
def test_single_signal_alpha_model(signal, expected_signals):
    """
    Checks that the single signal alpha model correctly produces
    the same signal for each asset in the universe.
    """
    universe = Mock()
    universe.get_assets.return_value = ['EQ:SPY', 'EQ:AGG', 'EQ:GLD']

    alpha = SingleSignalAlphaModel(universe=universe, signal=signal)
    dt = pd.Timestamp('2019-01-01 15:00:00', tz=pytz.utc)

    assert alpha(dt) == expected_signals
