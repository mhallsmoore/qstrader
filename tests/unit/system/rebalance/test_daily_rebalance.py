import pandas as pd
import pytest
import pytz

from qstrader.system.rebalance.daily import DailyRebalance


@pytest.mark.parametrize(
    "start_date,end_date,pre_market,expected_dates,expected_time",
    [
        (
            '2020-03-11', '2020-03-17', False, [
                '2020-03-11', '2020-03-12', '2020-03-13',
                '2020-03-16', '2020-03-17'
            ], '21:00:00'
        ),
        (
            '2019-12-26', '2020-01-07', True, [
                '2019-12-26', '2019-12-27', '2019-12-30',
                '2019-12-31', '2020-01-01', '2020-01-02',
                '2020-01-03', '2020-01-06', '2020-01-07'
            ], '14:30:00'
        )
    ]
)
def test_daily_rebalance(
    start_date, end_date, pre_market, expected_dates, expected_time
):
    """
    Checks that the daily rebalance provides the correct business
    datetimes for the provided range.
    """
    sd = pd.Timestamp(start_date, tz=pytz.UTC)
    ed = pd.Timestamp(end_date, tz=pytz.UTC)
    reb = DailyRebalance(start_date=sd, end_date=ed, pre_market=pre_market)
    actual_datetimes = reb._generate_rebalances()
    expected_datetimes = [
        pd.Timestamp('%s %s' % (expected_date, expected_time), tz=pytz.UTC)
        for expected_date in expected_dates
    ]

    assert actual_datetimes == expected_datetimes
