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

    def __eq__(self, rhs):
        """
        Two SimulationEvent entities are equal if they share
        the same timestamp and event type.

        Parameters
        ----------
        rhs : `SimulationEvent`
            The comparison SimulationEvent.

        Returns
        -------
        `boolean`
            Whether the two SimulationEvents are equal.
        """
        if self.ts != rhs.ts:
            return False
        if self.event_type != rhs.event_type:
            return False
        return True
