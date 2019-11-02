import pandas as pd
import pytest
import pytz

from qstrader.portcon.optimiser.fixed_weight import (
    FixedWeightPortfolioOptimiser
)


class DataHandlerMock(object):
    pass


@pytest.mark.parametrize(
    "initial_weights,expected_weights",
    [
        (
            {
                'EQ:ABCD': 0.25,
                'EQ:DEFG': 0.75
            },
            {
                'EQ:ABCD': 0.25,
                'EQ:DEFG': 0.75
            },
        ),
        (
            {
                'EQ:HIJK': 0.15,
                'EQ:LMNO': 0.45,
                'EQ:PQRS': 0.40
            },
            {
                'EQ:HIJK': 0.15,
                'EQ:LMNO': 0.45,
                'EQ:PQRS': 0.40
            }
        )
    ]
)
def test_fixed_weight_optimiser(initial_weights, expected_weights):
    """
    Tests initialisation and 'pass through' capability of
    FixedWeightPortfolioOptimiser.
    """
    dt = pd.Timestamp('2019-01-01 00:00:00', tz=pytz.UTC)
    data_handler = DataHandlerMock()
    fwo = FixedWeightPortfolioOptimiser(data_handler=data_handler)
    assert fwo(dt, initial_weights) == expected_weights
