import pandas as pd
import pytest
import pytz

from qstrader.simulation.daily_bday import DailyBusinessDaySimulationEngine
from qstrader.simulation.event import SimulationEvent


@pytest.mark.parametrize(
    "starting_day,ending_day,pre_market,post_market,expected_events",
    [
        (
            '2020-01-01', '2020-01-07', True, True,
            [
                ('2020-01-01 00:00:00', 'pre_market'),
                ('2020-01-01 14:30:00', 'market_open'),
                ('2020-01-01 21:00:00', 'market_close'),
                ('2020-01-01 23:59:00', 'post_market'),
                ('2020-01-02 00:00:00', 'pre_market'),
                ('2020-01-02 14:30:00', 'market_open'),
                ('2020-01-02 21:00:00', 'market_close'),
                ('2020-01-02 23:59:00', 'post_market'),
                ('2020-01-03 00:00:00', 'pre_market'),
                ('2020-01-03 14:30:00', 'market_open'),
                ('2020-01-03 21:00:00', 'market_close'),
                ('2020-01-03 23:59:00', 'post_market'),
                ('2020-01-06 00:00:00', 'pre_market'),
                ('2020-01-06 14:30:00', 'market_open'),
                ('2020-01-06 21:00:00', 'market_close'),
                ('2020-01-06 23:59:00', 'post_market'),
                ('2020-01-07 00:00:00', 'pre_market'),
                ('2020-01-07 14:30:00', 'market_open'),
                ('2020-01-07 21:00:00', 'market_close'),
                ('2020-01-07 23:59:00', 'post_market'),
            ]
        ),
        (
            '2020-01-01', '2020-01-07', False, False,
            [
                ('2020-01-01 14:30:00', 'market_open'),
                ('2020-01-01 21:00:00', 'market_close'),
                ('2020-01-02 14:30:00', 'market_open'),
                ('2020-01-02 21:00:00', 'market_close'),
                ('2020-01-03 14:30:00', 'market_open'),
                ('2020-01-03 21:00:00', 'market_close'),
                ('2020-01-06 14:30:00', 'market_open'),
                ('2020-01-06 21:00:00', 'market_close'),
                ('2020-01-07 14:30:00', 'market_open'),
                ('2020-01-07 21:00:00', 'market_close'),
            ]
        )
    ]
)
def test_daily_rebalance(
    starting_day, ending_day, pre_market, post_market, expected_events
):
    """
    Checks that the daily business day event generation provides
    the correct SimulationEvents for the given parameters.
    """
    sd = pd.Timestamp(starting_day, tz=pytz.UTC)
    ed = pd.Timestamp(ending_day, tz=pytz.UTC)

    sim_engine = DailyBusinessDaySimulationEngine(sd, ed, pre_market, post_market)

    for sim_events in zip(sim_engine, expected_events):
        calculated_event = sim_events[0]
        expected_event = SimulationEvent(pd.Timestamp(sim_events[1][0], tz=pytz.UTC), sim_events[1][1])
        assert calculated_event == expected_event
