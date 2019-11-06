from qstrader.system.rebalance.rebalance import Rebalance


class BuyAndHoldRebalance(Rebalance):
    """
    Generates a single rebalance timestamp at the start date in
    order to create a single set of orders at the beginning of
    a backtest, with no further rebalances carried out.

    Parameters
    ----------
    start_dt : `pd.Timestamp`
        The starting datetime of the buy and hold rebalance.
    """

    def __init__(self, start_dt):
        self.start_dt = start_dt
        self.rebalances = [start_dt]
