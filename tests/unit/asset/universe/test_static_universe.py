import pandas as pd
import pytest
import pytz

from qstrader.asset.universe.static import StaticUniverse


@pytest.mark.parametrize(
    'assets,dt,expected',
    [
        (
            ['EQ:SPY', 'EQ:AGG'],
            pd.Timestamp('2019-01-01 15:00:00', tz=pytz.utc),
            ['EQ:SPY', 'EQ:AGG']
        ),
        (
            ['EQ:GLD', 'EQ:GSG', 'EQ:TLT'],
            pd.Timestamp('2020-05-01 15:00:00', tz=pytz.utc),
            ['EQ:GLD', 'EQ:GSG', 'EQ:TLT']
        )
    ]
)
def test_static_universe(assets, dt, expected):
    """
    Checks that the StaticUniverse correctly returns the
    list of assets for a particular datetime.
    """
    universe = StaticUniverse(assets)
    assert universe.get_assets(dt) == expected
