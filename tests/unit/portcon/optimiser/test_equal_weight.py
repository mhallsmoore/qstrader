import pandas as pd
import pytest
import pytz

from qstrader.portcon.optimiser.equal_weight import (
    EqualWeightPortfolioOptimiser
)


class DataHandlerMock(object):
    pass


@pytest.mark.parametrize(
    "scale,initial_weights,expected_weights",
    [
        (
            1.0,
            {
                'EQ:ABCD': 0.25,
                'EQ:DEFG': 0.75
            },
            {
                'EQ:ABCD': 0.5,
                'EQ:DEFG': 0.5
            },
        ),
        (
            2.0,
            {
                'EQ:HIJK': 0.15,
                'EQ:LMNO': 0.45,
                'EQ:PQRS': 0.40
            },
            {
                'EQ:HIJK': 2 / 3.0,
                'EQ:LMNO': 2 / 3.0,
                'EQ:PQRS': 2 / 3.0
            }
        )
    ]
)
def test_fixed_weight_optimiser(scale, initial_weights, expected_weights):
    """
    Tests initialisation and 'pass through' capability of
    FixedWeightPortfolioOptimiser.
    """
    dt = pd.Timestamp('2019-01-01 00:00:00', tz=pytz.UTC)
    data_handler = DataHandlerMock()
    fwo = EqualWeightPortfolioOptimiser(scale=scale, data_handler=data_handler)
    assert fwo(dt, initial_weights) == expected_weights
