import numpy as np


class Transaction(object):
    """
    Handles the transaction of an asset, as used in the
    Position class.

    Parameters
    ----------
    asset : `str`
        The asset symbol of the transaction
    quantity : `int`
        Whole number quantity of shares in the transaction
    dt : `pd.Timestamp`
        The date/time of the transaction
    price : `float`
        The transaction price carried out
    order_id : `int`
        The unique order identifier
    commission : `float`, optional
        The trading commission
    """

    def __init__(
        self,
        asset,
        quantity,
        dt,
        price,
        order_id,
        commission=None
    ):
        self.asset = asset
        self.quantity = quantity
        self.direction = np.copysign(1, self.quantity)
        self.dt = dt
        self.price = price
        self.order_id = order_id
        self.commission = commission

    def __repr__(self):
        """
        Provides a representation of the Transaction
        to allow full recreation of the object.

        Returns
        -------
        `str`
            The string representation of the Transaction.
        """
        return "%s(asset=%s, quantity=%s, dt=%s, " \
            "price=%s, order_id=%s)" % (
                type(self).__name__, self.asset,
                self.quantity, self.dt,
                self.price, self.order_id
            )
