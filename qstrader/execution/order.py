import uuid

import numpy as np


class Order(object):
    """
    Represents sending an order from a trading algo entity
    to a brokerage to execute.

    A commission can be added here to override the commission
    model, if known. An order_id can be added if required,
    otherwise it will be randomly assigned.

    Parameters
    ----------
    dt : `pd.Timestamp`
        The date-time that the order was created.
    asset : `Asset`
        The asset to transact with the order.
    quantity : `int`
        The quantity of the asset to transact.
        A negative quantity means a short.
    commission : `float`, optional
        If commission is known it can be added.
    order_id : `str`, optional
        The order ID of the order, if known.
    """

    def __init__(
        self,
        dt,
        asset,
        quantity,
        commission=0.0,
        order_id=None
    ):
        self.created_dt = dt
        self.cur_dt = dt
        self.asset = asset
        self.quantity = quantity
        self.commission = commission
        self.direction = np.copysign(1, self.quantity)
        self.order_id = self._set_or_generate_order_id(order_id)

    def _order_attribs_equal(self, other):
        """
        Asserts whether all attributes of the Order are equal
        with the exception of the order ID.

        Used primarily for testing that orders are generated correctly.

        Parameters
        ----------
        other : `Order`
            The order to compare attribute equality to.

        Returns
        -------
        `Boolean`
            Whether the non-order ID attributes are equal.
        """
        if self.created_dt != other.created_dt:
            return False
        if self.cur_dt != other.cur_dt:
            return False
        if self.asset != other.asset:
            return False
        if self.quantity != other.quantity:
            return False
        if self.commission != other.commission:
            return False
        if self.direction != other.direction:
            return False
        return True

    def __repr__(self):
        """
        Output a string representation of the object

        Returns
        -------
        `str`
            String representation of the Order instance.
        """
        return (
            "Order(dt='%s', asset='%s', quantity=%s, "
            "commission=%s, direction=%s, order_id=%s)" % (
                self.created_dt, self.asset, self.quantity,
                self.commission, self.direction, self.order_id
            )
        )

    def _set_or_generate_order_id(self, order_id=None):
        """
        Sets or generates a unique order ID for the order, using a UUID.

        Parameters
        ----------
        order_id : `str`, optional
            An optional order ID override.

        Returns
        -------
        `str`
            The order ID string for the Order.
        """
        if order_id is None:
            return uuid.uuid4().hex
        else:
            return order_id
