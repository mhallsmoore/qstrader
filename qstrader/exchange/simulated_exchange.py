import datetime

from qstrader.exchange.exchange import Exchange


class SimulatedExchange(Exchange):
    """
    The SimulatedExchange class is used to model a live
    trading venue.

    It exposes methods to inform a client class intance of
    when the exchange is open to determine when orders can
    be executed.

    Parameters
    ----------
    start_dt : `pd.Timestamp`
        The starting time of the simulated exchange.
    """

    def __init__(self, start_dt):
        self.start_dt = start_dt

        # TODO: Eliminate hardcoding of NYSE
        # TODO: Make these timezone-aware
        self.open_dt = datetime.time(14, 30)
        self.close_dt = datetime.time(21, 00)

    def is_open_at_datetime(self, dt):
        """
        Check if the SimulatedExchange is open at a particular
        provided pandas Timestamp.

        This logic is simplistic in that it only checks whether
        the provided time is between market hours on a weekday.

        There is no historical calendar handling or concept of
        exchange holidays.

        Parameters
        ----------
        dt : `pd.Timestamp`
            The timestamp to check for open market hours.

        Returns
        -------
        `Boolean`
            Whether the exchange is open at this timestamp.
        """
        if dt.weekday() > 4:
            return False
        return self.open_dt <= dt.time() and dt.time() < self.close_dt
