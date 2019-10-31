from qstrader.broker.fee_model.fee_model import FeeModel


class ZeroFeeModel(FeeModel):
    """
    A FeeModel subclass that produces no commission, fees
    or taxes. This is the default fee model for simulated
    brokerages within QSTrader.
    """

    def __init__(self):
        pass

    def _calc_commission(self, asset, quantity, consideration, broker=None):
        """
        Returns zero commission.
        """
        return 0.0

    def _calc_tax(self, asset, quantity, consideration, broker=None):
        """
        Returns zero tax.
        """
        return 0.0

    def calc_total_cost(self, asset, quantity, consideration, broker=None):
        """
        Calculate the total of any commission and/or tax
        for the trade of size 'consideration'.
        """
        commission = self._calc_commission(asset, consideration, broker)
        tax = self._calc_tax(asset, consideration, broker)
        return commission + tax
