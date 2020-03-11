from qstrader.broker.fee_model.fee_model import FeeModel


class ZeroFeeModel(FeeModel):
    """
    A FeeModel subclass that produces no commission, fees
    or taxes. This is the default fee model for simulated
    brokerages within QSTrader.
    """

    def _calc_commission(self, asset, quantity, consideration, broker=None):
        """
        Returns zero commission.

        Parameters
        ----------
        asset : `str`
            The asset symbol string.
        quantity : `int`
            The quantity of assets (needed for InteractiveBrokers
            style calculations).
        consideration : `float`
            Price times quantity of the order.
        broker : `Broker`, optional
            An optional Broker reference.

        Returns
        -------
        `float`
            The zero-cost commission.
        """
        return 0.0

    def _calc_tax(self, asset, quantity, consideration, broker=None):
        """
        Returns zero tax.

        Parameters
        ----------
        asset : `str`
            The asset symbol string.
        quantity : `int`
            The quantity of assets (needed for InteractiveBrokers
            style calculations).
        consideration : `float`
            Price times quantity of the order.
        broker : `Broker`, optional
            An optional Broker reference.

        Returns
        -------
        `float`
            The zero-cost tax.
        """
        return 0.0

    def calc_total_cost(self, asset, quantity, consideration, broker=None):
        """
        Calculate the total of any commission and/or tax
        for the trade of size 'consideration'.

        Parameters
        ----------
        asset : `str`
            The asset symbol string.
        quantity : `int`
            The quantity of assets (needed for InteractiveBrokers
            style calculations).
        consideration : `float`
            Price times quantity of the order.
        broker : `Broker`, optional
            An optional Broker reference.

        Returns
        -------
        `float`
            The zero-cost total commission and tax.
        """
        commission = self._calc_commission(asset, quantity, consideration, broker)
        tax = self._calc_tax(asset, quantity, consideration, broker)
        return commission + tax
