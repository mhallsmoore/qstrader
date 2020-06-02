import pandas as pd
import pytest
import pytz

from qstrader.simulation.event import SimulationEvent


@pytest.mark.parametrize(
    "sim_event_params,compare_event_params,expected_result",
    [
        (
            ('2020-01-01 00:00:00', 'pre_market'),
            ('2020-01-01 00:00:00', 'pre_market'),
            True,
        ),
        (
            ('2020-01-01 00:00:00', 'pre_market'),
            ('2020-01-01 00:00:00', 'post_market'),
            False,
        ),
        (
            ('2020-01-01 00:00:00', 'pre_market'),
            ('2020-01-02 00:00:00', 'pre_market'),
            False,
        ),
        (
            ('2020-01-01 00:00:00', 'pre_market'),
            ('2020-01-02 00:00:00', 'post_market'),
            False,
        )
    ]
)
def test_sim_event_eq(
    sim_event_params, compare_event_params, expected_result
):
    """
    Checks that the SimulationEvent __eq__ correctly
    compares SimulationEvent instances.
    """
    sim_event = SimulationEvent(pd.Timestamp(sim_event_params[0], tz=pytz.UTC), sim_event_params[1])
    compare_event = SimulationEvent(pd.Timestamp(compare_event_params[0], tz=pytz.UTC), compare_event_params[1])

    assert expected_result == (sim_event == compare_event)
