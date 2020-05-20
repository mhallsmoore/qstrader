import pandas as pd
import pytest
import pytz

from qstrader.system.rebalance.end_of_month import EndOfMonthRebalance


@pytest.mark.parametrize(
    "start_date,end_date,pre_market,expected_dates,expected_time",
    [
        (
            '2020-03-11', '2020-12-31', False, [
                '2020-03-31', '2020-04-30', '2020-05-29', '2020-06-30',
                '2020-07-31', '2020-08-31', '2020-09-30', '2020-10-30',
                '2020-11-30', '2020-12-31'
            ], '21:00:00'
        ),
        (
            '2019-12-26', '2020-09-01', True, [
                '2019-12-31', '2020-01-31', '2020-02-28', '2020-03-31',
                '2020-04-30', '2020-05-29', '2020-06-30', '2020-07-31',
                '2020-08-31'
            ], '14:30:00'
        )
    ]
)
def test_monthly_rebalance(
    start_date, end_date, pre_market, expected_dates, expected_time
):
    """
    Checks that the end of month (business day) rebalance provides
    the correct datetimes for the provided range.
    """
    sd = pd.Timestamp(start_date, tz=pytz.UTC)
    ed = pd.Timestamp(end_date, tz=pytz.UTC)

    reb = EndOfMonthRebalance(
        start_dt=sd, end_dt=ed, pre_market=pre_market
    )

    actual_datetimes = reb._generate_rebalances()

    expected_datetimes = [
        pd.Timestamp('%s %s' % (expected_date, expected_time), tz=pytz.UTC)
        for expected_date in expected_dates
    ]

    assert actual_datetimes == expected_datetimes
