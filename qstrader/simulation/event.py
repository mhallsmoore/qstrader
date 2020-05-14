class SimulationEvent(object):
    """
    Stores a timestamp and event type string associated with
    a simulation event.

    Parameters
    ----------
    ts : `pd.Timestamp`
        The timestamp of the simulation event.
    event_type : `str`
        The event type string.
    """

    def __init__(self, ts, event_type):
        self.ts = ts
        self.event_type = event_type
