import pandas as pd
import pytz

from qstrader.system.rebalance.rebalance import Rebalance


class WeeklyRebalance(Rebalance):
    """
    Generates a list of rebalance timestamps for pre- or post-market,
    for a particular trading day of the week between the starting and
    ending dates provided.

    All timestamps produced are set to UTC.
    """

    def __init__(
        self,
        start_date,
        end_date,
        weekday,
        pre_market=False
    ):
        """
        Initialise the WeeklyRebalance instance.
        """
        self.weekday = self._set_weekday(weekday)
        self.start_date = start_date
        self.end_date = end_date
        self.pre_market_time = self._set_market_time(pre_market)
        self.rebalances = self._generate_rebalances()

    def _set_weekday(self, weekday):
        """
        Checks that the weekday string corresponds to
        a business weekday.
        """
        weekdays = ("MON", "TUE", "WED", "THU", "FRI")
        if weekday.upper() not in weekdays:
            raise ValueError(
                "Provided weekday keyword '%s' is not recognised "
                "or not a valid weekday." % weekday
            )
        else:
            return weekday.upper()

    def _set_market_time(self, pre_market):
        """
        """
        return "00:00:00" if pre_market else "23:59:00"

    def _generate_rebalances(self):
        """
        """
        rebalance_dates = pd.date_range(
            start=self.start_date,
            end=self.end_date,
            freq='W-%s' % self.weekday
        )

        rebalance_times = [
            pd.Timestamp(
                "%s %s" % (date, self.pre_market_time), tz=pytz.utc
            )
            for date in rebalance_dates
        ]

        return rebalance_times
