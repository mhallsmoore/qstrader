import pandas as pd
import pytest
import pytz

from qstrader.system.rebalance.weekly import WeeklyRebalance


@pytest.mark.parametrize(
    "start_date,end_date,weekday,pre_market,expected_dates,expected_time",
    [
        (
            '2020-03-11', '2020-05-17', 'MON', False, [
                '2020-03-16', '2020-03-23', '2020-03-30', '2020-04-06',
                '2020-04-13', '2020-04-20', '2020-04-27', '2020-05-04',
                '2020-05-11'
            ], '21:00:00'
        ),
        (
            '2019-12-26', '2020-02-07', 'WED', True, [
                '2020-01-01', '2020-01-08', '2020-01-15', '2020-01-22',
                '2020-01-29', '2020-02-05'
            ], '14:30:00'
        )
    ]
)
def test_weekly_rebalance(
    start_date, end_date, weekday, pre_market, expected_dates, expected_time
):
    """
    Checks that the weekly rebalance provides the correct business
    datetimes for the provided range.
    """
    sd = pd.Timestamp(start_date, tz=pytz.UTC)
    ed = pd.Timestamp(end_date, tz=pytz.UTC)

    reb = WeeklyRebalance(
        start_date=sd, end_date=ed, weekday=weekday, pre_market=pre_market
    )

    actual_datetimes = reb._generate_rebalances()

    expected_datetimes = [
        pd.Timestamp('%s %s' % (expected_date, expected_time), tz=pytz.UTC)
        for expected_date in expected_dates
    ]

    assert actual_datetimes == expected_datetimes


def test_check_weekday_raises_value_error():
    """
    Checks that initialisation of WeeklyRebalance raises
    a ValueError if the weekday string is in the incorrect
    format.
    """
    sd = pd.Timestamp('2020-01-01', tz=pytz.UTC)
    ed = pd.Timestamp('2020-02-01', tz=pytz.UTC)
    pre_market = True
    weekday = 'SUN'

    with pytest.raises(ValueError):
        WeeklyRebalance(
            start_date=sd, end_date=ed, weekday=weekday, pre_market=pre_market
        )
