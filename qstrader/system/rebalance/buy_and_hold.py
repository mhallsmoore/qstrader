import pandas as pd
from pandas.tseries.offsets import BusinessDay
from qstrader.system.rebalance.rebalance import Rebalance


class BuyAndHoldRebalance(Rebalance):
    """
    Generates a single rebalance timestamp at the first business day 
    after the start date. Creates a single set of orders at the beginning of
    a backtest, with no further rebalances carried out.

    Parameters
    ----------
    start_dt : `pd.Timestamp`
        The starting datetime of the buy and hold rebalance.
    """

    def __init__(self, start_dt):
        self.start_dt = start_dt
        self.rebalances = self._generate_rebalances()

    def _is_business_day(self):
        """
        Checks if the start_dt is a business day.
        
        Returns
        -------
        `boolean`
        """
        return bool(len(pd.bdate_range(self.start_dt, self.start_dt)))

    def _generate_rebalances(self):
        """
        Outputs the rebalance timestamp offset to the next
        business day.

        Does not include holidays.

        Returns
        -------
        `list[pd.Timestamp]`
            The rebalance timestamp list.
        """
        if not self._is_business_day():
            rebalance_date = self.start_dt + BusinessDay()
        else:
            rebalance_date = self.start_dt
        return [rebalance_date]
