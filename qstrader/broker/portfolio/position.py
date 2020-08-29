from math import floor

import numpy as np


class Position(object):
    """
    Handles the accounting of entering a new position in an
    Asset along with subsequent modifications via additional
    trades.

    The approach taken here separates the long and short side
    for accounting purposes. It also includes an unrealised and
    realised running profit & loss of the position.

    Parameters
    ----------
    asset : `str`
        The Asset symbol string.
    current_price : `float`
        The initial price of the Position.
    current_dt : `pd.Timestamp`
        The time at which the Position was created.
    buy_quantity : `int`
        The amount of the asset bought.
    sell_quantity : `int`
        The amount of the asset sold.
    avg_bought : `float`
        The initial price paid for buying assets.
    avg_sold : `float`
        The initial price paid for selling assets.
    buy_commission : `float`
        The commission spent on buying assets for this position.
    sell_commission : `float`
        The commission spent on selling assets for this position.
    """

    def __init__(
        self,
        asset,
        current_price,
        current_dt,
        buy_quantity,
        sell_quantity,
        avg_bought,
        avg_sold,
        buy_commission,
        sell_commission
    ):
        self.asset = asset
        self.current_price = current_price
        self.current_dt = current_dt
        self.buy_quantity = buy_quantity
        self.sell_quantity = sell_quantity
        self.avg_bought = avg_bought
        self.avg_sold = avg_sold
        self.buy_commission = buy_commission
        self.sell_commission = sell_commission

    @classmethod
    def open_from_transaction(cls, transaction):
        """
        Constructs a new Position instance from the provided
        Transaction.

        Parameters
        ----------
        transaction : `Transaction`
            The transaction with which to open the Position.

        Returns
        -------
        `Position`
            The instantiated position.
        """
        asset = transaction.asset
        current_price = transaction.price
        current_dt = transaction.dt

        if transaction.quantity > 0:
            buy_quantity = transaction.quantity
            sell_quantity = 0
            avg_bought = current_price
            avg_sold = 0.0
            buy_commission = transaction.commission
            sell_commission = 0.0
        else:
            buy_quantity = 0
            sell_quantity = -1.0 * transaction.quantity
            avg_bought = 0.0
            avg_sold = current_price
            buy_commission = 0.0
            sell_commission = transaction.commission

        return cls(
            asset,
            current_price,
            current_dt,
            buy_quantity,
            sell_quantity,
            avg_bought,
            avg_sold,
            buy_commission,
            sell_commission
        )

    def _check_set_dt(self, dt):
        """
        Checks that the provided timestamp is valid and if so sets
        the new current time of the Position.

        Parameters
        ----------
        dt : `pd.Timestamp`
            The timestamp to be checked and potentially used as
            the new current time.
        """
        if dt is not None:
            if (dt < self.current_dt):
                raise ValueError(
                    'Supplied update time of "%s" is earlier than '
                    'the current time of "%s".' % (dt, self.current_dt)
                )
            else:
                self.current_dt = dt

    @property
    def direction(self):
        """
        Returns an integer value representing the direction.

        Returns
        -------
        `int`
            1 - Long, 0 - No direction, -1 - Short.
        """
        if self.net_quantity == 0:
            return 0
        else:
            return np.copysign(1, self.net_quantity)

    @property
    def market_value(self):
        """
        Return the market value (respecting the direction) of the
        Position based on the current price available to the Position.

        Returns
        -------
        `float`
            The current market value of the Position.
        """
        return self.current_price * self.net_quantity

    @property
    def avg_price(self):
        """
        The average price paid for all assets on the long or short side.

        Returns
        -------
        `float`
            The average price on either the long or short side.
        """
        if self.net_quantity == 0:
            return 0.0
        elif self.net_quantity > 0:
            return (self.avg_bought * self.buy_quantity + self.buy_commission) / self.buy_quantity
        else:
            return (self.avg_sold * self.sell_quantity - self.sell_commission) / self.sell_quantity

    @property
    def net_quantity(self):
        """
        The difference in the quantity of assets bought and sold to date.

        Returns
        -------
        `int`
            The net quantity of assets.
        """
        return self.buy_quantity - self.sell_quantity

    @property
    def total_bought(self):
        """
        Calculates the total average cost of assets bought.

        Returns
        -------
        `float`
            The total average cost of assets bought.
        """
        return self.avg_bought * self.buy_quantity

    @property
    def total_sold(self):
        """
        Calculates the total average cost of assets sold.

        Returns
        -------
        `float`
            The total average cost of assets solds.
        """
        return self.avg_sold * self.sell_quantity

    @property
    def net_total(self):
        """
        Calculates the net total average cost of assets
        bought and sold.

        Returns
        -------
        `float`
            The net total average cost of assets bought
            and sold.
        """
        return self.total_sold - self.total_bought

    @property
    def commission(self):
        """
        Calculates the total commission from assets bought and sold.

        Returns
        -------
        `float`
            The total commission from assets bought and sold.
        """
        return self.buy_commission + self.sell_commission

    @property
    def net_incl_commission(self):
        """
        Calculates the net total average cost of assets bought
        and sold including the commission.

        Returns
        -------
        `float`
            The net total average cost of assets bought and
            sold including the commission.
        """
        return self.net_total - self.commission

    @property
    def realised_pnl(self):
        """
        Calculates the profit & loss (P&L) that has been 'realised' via
        two opposing asset transactions in the Position to date.

        Returns
        -------
        `float`
            The calculated realised P&L.
        """
        if self.direction == 1:
            if self.sell_quantity == 0:
                return 0.0
            else:
                return (
                    ((self.avg_sold - self.avg_bought) * self.sell_quantity) -
                    ((self.sell_quantity / self.buy_quantity) * self.buy_commission) -
                    self.sell_commission
                )
        elif self.direction == -1:
            if self.buy_quantity == 0:
                return 0.0
            else:
                return (
                    ((self.avg_sold - self.avg_bought) * self.buy_quantity) -
                    ((self.buy_quantity / self.sell_quantity) * self.sell_commission) -
                    self.buy_commission
                )
        else:
            return self.net_incl_commission

    @property
    def unrealised_pnl(self):
        """
        Calculates the profit & loss (P&L) that has yet to be 'realised'
        in the remaining non-zero quantity of assets, due to the current
        market price.

        Returns
        -------
        `float`
            The calculated unrealised P&L.
        """
        return (self.current_price - self.avg_price) * self.net_quantity

    @property
    def total_pnl(self):
        """
        Calculates the sum of the unrealised and realised profit & loss (P&L).

        Returns
        -------
        `float`
            The sum of the unrealised and realised P&L.
        """
        return self.realised_pnl + self.unrealised_pnl

    def update_current_price(self, market_price, dt=None):
        """
        Updates the Position's awareness of the current market price
        of the Asset, with an optional timestamp.

        Parameters
        ----------
        market_price : `float`
            The current market price.
        dt : `pd.Timestamp`, optional
            The optional timestamp of the current market price.
        """
        self._check_set_dt(dt)

        if market_price <= 0.0:
            raise ValueError(
                'Market price "%s" of asset "%s" must be positive to '
                'update the position.' % (market_price, self.asset)
            )
        else:
            self.current_price = market_price

    def _transact_buy(self, quantity, price, commission):
        """
        Handle the accounting for creating a new long leg for the
        Position.

        Parameters
        ----------
        quantity : `int`
            The additional quantity of assets to purchase.
        price : `float`
            The price at which this leg was purchased.
        commission : `float`
            The commission paid to the broker for the purchase.
        """
        self.avg_bought = ((self.avg_bought * self.buy_quantity) + (quantity * price)) / (self.buy_quantity + quantity)
        self.buy_quantity += quantity
        self.buy_commission += commission

    def _transact_sell(self, quantity, price, commission):
        """
        Handle the accounting for creating a new short leg for the
        Position.

        Parameters
        ----------
        quantity : `int`
            The additional quantity of assets to sell.
        price : `float`
            The price at which this leg was sold.
        commission : `float`
            The commission paid to the broker for the sale.
        """
        self.avg_sold = ((self.avg_sold * self.sell_quantity) + (quantity * price)) / (self.sell_quantity + quantity)
        self.sell_quantity += quantity
        self.sell_commission += commission

    def transact(self, transaction):
        """
        Calculates the adjustments to the Position that occur
        once new units in an Asset are bought and sold.

        Parameters
        ----------
        transaction : `Transaction`
            The Transaction to update the Position with.
        """
        if self.asset != transaction.asset:
            raise ValueError(
                'Failed to update Position with asset %s when '
                'carrying out transaction in asset %s. ' % (
                    self.asset, transaction.asset
                )
            )

        # Nothing to do if the transaction has no quantity
        if int(floor(transaction.quantity)) == 0:
            return

        # Depending upon the direction of the transaction
        # ensure the correct calculation is called
        if transaction.quantity > 0:
            self._transact_buy(
                transaction.quantity,
                transaction.price,
                transaction.commission
            )
        else:
            self._transact_sell(
                -1.0 * transaction.quantity,
                transaction.price,
                transaction.commission
            )

        # Update the current trade information
        self.update_current_price(transaction.price, transaction.dt)
        self.current_dt = transaction.dt
