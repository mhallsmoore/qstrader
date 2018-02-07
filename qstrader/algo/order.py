# The MIT License (MIT)
#
# Copyright (c) 2015 QuantStart.com, QuarkGluon Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import uuid

import numpy as np


class Order(object):
    """Represents sending an order from a trading algo entity
    to a brokerage to execute.

    A commission can be added here to override the commission
    model, if known. An order_id can be added if required,
    otherwise it will be randomly assigned.

    Parameters
    ----------
    dt : datetime
        The datetime that the order was created.
    asset : Asset
        The asset to transact with the order.
    quantity : int
        The quantity of the asset to transact.
        A negative quantity means a short.
    commission : float, optional
        If commission is known it can be added.
    order_id : str, optional
        The order ID of the order, if known.
    """

    def __init__(
        self, dt, asset, quantity, limit_price=None,
        stop_price=None, commission=0.0, order_id=None
    ):
        """
        Initialise the order object.
        """
        self.created_dt = dt
        self.cur_dt = dt
        self.asset = asset
        self.quantity = quantity
        self.commission = commission
        self.direction = np.copysign(1, self.quantity)
        self.order_id = self._set_order_id(order_id)

    def __repr__(self):
        """
        Output a string representation of the object
        """
        return (
            "Order(dt='%s', asset='%s', quantity=%s, "
            "commission=%s, direction=%s, order_id=%s)" % (
                self.created_dt, self.asset.name, self.quantity,
                self.commission, self.direction, self.order_id
            )
        )

    def _set_order_id(self, order_id):
        if order_id is None:
            return uuid.uuid4().hex
        else:
            return order_id
