import pandas as pd
import pytz

from qstrader.system.rebalance.rebalance import Rebalance


class EndOfMonthRebalance(Rebalance):
    """
    Generates a list of rebalance timestamps for pre- or post-market,
    for the final calendar day of the month between the starting and
    ending dates provided.

    All timestamps produced are set to UTC.

    Parameters
    ----------
    start_dt : `pd.Timestamp`
        The starting datetime of the rebalance range.
    end_dt : `pd.Timestamp`
        The ending datetime of the rebalance range.
    pre_market : `Boolean`, optional
        Whether to carry out the rebalance at market open/close on
        the final day of the month. Defaults to False, i.e at
        market close.
    """

    def __init__(
        self,
        start_dt,
        end_dt,
        pre_market=False
    ):
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.market_time = self._set_market_time(pre_market)
        self.rebalances = self._generate_rebalances()

    def _set_market_time(self, pre_market):
        """
        Determines whether to use market open or market close
        as the rebalance time.

        Parameters
        ----------
        pre_market : `Boolean`
            Whether the rebalance is carried out at market open/close.

        Returns
        -------
        `str`
            The time string used for Pandas timestamp construction.
        """
        return "14:30:00" if pre_market else "21:00:00"

    def _generate_rebalances(self):
        """
        Utilise the Pandas date_range method to create the appropriate
        list of rebalance timestamps.

        Returns
        -------
        `List[pd.Timestamp]`
            The list of rebalance timestamps.
        """
        rebalance_dates = pd.date_range(
            start=self.start_dt,
            end=self.end_dt,
            freq='BM'
        )

        rebalance_times = [
            pd.Timestamp(
                "%s %s" % (date, self.market_time), tz=pytz.utc
            )
            for date in rebalance_dates
        ]
        return rebalance_times
