from unittest.mock import Mock

import pandas as pd
import pytest
import pytz

from qstrader.alpha_model.fixed_signals import FixedSignalsAlphaModel


@pytest.mark.parametrize(
    'signals',
    [
        ({'EQ:SPY': 0.75, 'EQ:AGG': 0.75, 'EQ:GLD': 0.75}),
        ({'EQ:SPY': -0.25, 'EQ:AGG': -0.25, 'EQ:GLD': -0.25})
    ]
)
def test_fixed_signals_alpha_model(signals):
    """
    Checks that the fixed signals alpha model correctly produces
    the same signals for each asset in the universe.
    """
    universe = Mock()
    universe.get_assets.return_value = ['EQ:SPY', 'EQ:AGG', 'EQ:GLD']

    alpha = FixedSignalsAlphaModel(universe=universe, signal_weights=signals)
    dt = pd.Timestamp('2019-01-01 15:00:00', tz=pytz.utc)

    assert alpha(dt) == signals
