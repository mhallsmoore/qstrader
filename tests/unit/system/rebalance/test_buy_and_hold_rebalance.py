import pandas as pd
import pytest
import pytz

from qstrader.system.rebalance.buy_and_hold import BuyAndHoldRebalance


@pytest.mark.parametrize(
    "start_dt, reb_dt", [
        ('2020-01-01', '2020-01-01'), 
        ('2020-02-02', '2020-02-03')
    ],
)
def test_buy_and_hold_rebalance(start_dt, reb_dt):
    """
    Checks that the buy and hold rebalance sets the
    appropriate rebalance dates, both for a business and 
    a non-business day.

    Does not include holidays.
    """
    sd = pd.Timestamp(start_dt, tz=pytz.UTC)
    rd = pd.Timestamp(reb_dt, tz=pytz.UTC)
    reb = BuyAndHoldRebalance(start_dt=sd)

    assert reb.start_dt == sd
    assert reb.rebalances == [rd]
