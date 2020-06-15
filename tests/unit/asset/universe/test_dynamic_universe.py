import pandas as pd
import pytest
import pytz

from qstrader.asset.universe.dynamic import DynamicUniverse


@pytest.mark.parametrize(
    'asset_dates,dt,expected',
    [
        (
            {
                'EQ:SPY': pd.Timestamp('1993-01-01 14:30:00', tz=pytz.utc),
                'EQ:AGG': pd.Timestamp('2003-01-01 14:30:00', tz=pytz.utc),
                'EQ:TLT': pd.Timestamp('2012-01-01 14:30:00', tz=pytz.utc)
            },
            pd.Timestamp('1990-01-01 14:30:00', tz=pytz.utc),
            []
        ),
        (
            {
                'EQ:SPY': pd.Timestamp('1993-01-01 14:30:00', tz=pytz.utc),
                'EQ:AGG': pd.Timestamp('2003-01-01 14:30:00', tz=pytz.utc),
                'EQ:TLT': pd.Timestamp('2012-01-01 14:30:00', tz=pytz.utc)
            },
            pd.Timestamp('1995-01-01 14:30:00', tz=pytz.utc),
            ['EQ:SPY']
        ),
        (
            {
                'EQ:SPY': pd.Timestamp('1993-01-01 14:30:00', tz=pytz.utc),
                'EQ:AGG': pd.Timestamp('2003-01-01 14:30:00', tz=pytz.utc),
                'EQ:TLT': pd.Timestamp('2012-01-01 14:30:00', tz=pytz.utc)
            },
            pd.Timestamp('2005-01-01 14:30:00', tz=pytz.utc),
            ['EQ:SPY', 'EQ:AGG']
        ),
        (
            {
                'EQ:SPY': pd.Timestamp('1993-01-01 14:30:00', tz=pytz.utc),
                'EQ:AGG': pd.Timestamp('2003-01-01 14:30:00', tz=pytz.utc),
                'EQ:TLT': pd.Timestamp('2012-01-01 14:30:00', tz=pytz.utc)
            },
            pd.Timestamp('2015-01-01 14:30:00', tz=pytz.utc),
            ['EQ:SPY', 'EQ:AGG', 'EQ:TLT']
        )
    ]
)
def test_dynamic_universe(asset_dates, dt, expected):
    """
    Checks that the DynamicUniverse correctly returns the
    list of assets for a particular datetime.
    """
    universe = DynamicUniverse(asset_dates)
    assert set(universe.get_assets(dt)) == set(expected)
