import numpy as np


class Position(object):
    """
    A class that keeps track of the position in an Asset
    as registered at a particular Broker, in a Portfolio.

    Includes the quantity of the position, the current trade
    price and the position book cost (VWAP per unit).

    Parameters
    ----------
    asset : `str`
        The asset symbol string of the position
    quantity : `int`, optional
        Whole number quantity of units in the position
    book_cost_pu : `float`, optional
        Volume weighted average price per unit of
        the asset (book cost per unit)
    current_price : `float`, optional
        The most recently known trade price of the asset
        on an Exchange, as known to the Position
    current_dt : datetime, optional
        The most recently known trade date of the asset
        on the exchange, as known to the Position
    """

    def __init__(
        self,
        asset,
        quantity=0.0,
        book_cost_pu=0.0,
        current_price=0.0,
        current_dt=None
    ):
        self.asset = asset
        self.quantity = quantity
        self.direction = np.copysign(1, self.quantity)
        self.book_cost_pu = book_cost_pu
        self.current_price = current_price
        self.current_dt = current_dt
        self.book_cost = self.book_cost_pu * self.quantity

    def __repr__(self):
        """
        Provides a representation of the Position object to allow
        full recreation of the object.

        Returns
        -------
        `str`
            The string representation of the Position.
        """
        return "%s(asset=%s, quantity=%s, book_cost_pu=%s, " \
            "current_price=%s)" % (
                self.__class__.__name__, self.asset, self.quantity,
                self.book_cost_pu, self.current_price
            )

    @property
    def market_value(self):
        """
        Return the market value of the position based on the
        current trade price provided.

        Returns
        -------
        `float`
            The current market value of the Position.
        """
        return self.current_price * self.quantity

    @property
    def unrealised_gain(self):
        """
        Calculate the unrealised absolute gain in currency
        of the position based solely on the market value.

        Returns
        -------
        `float`
            The unrealised gain of the Position.
        """
        return self.market_value - self.book_cost

    @property
    def unrealised_percentage_gain(self):
        """
        Calculate the unrealised percentage gain of the
        position based solely on the market value.

        Returns
        -------
        `float`
            The unrealised percentage gain of the Position.
        """
        if self.book_cost == 0.0:
            return 0.0
        return (self.direction * self.unrealised_gain / self.book_cost) * 100.0

    def update_book_cost_for_commission(self, asset, commission):
        """
        Handles the adjustment to the position book cost due to
        trading commissions.

        Parameters
        ----------
        asset : `str`
            The asset symbol string.
        commission : `float`
            The commission to be applied to the book cost.
        """
        if self.asset != asset:
            raise ValueError(
                'Failed to adjust book cost for Position on asset '
                '%s due to attempt being made to adjust asset %s.' % {
                    self.asset, asset
                }
            )

        # If there's no commission, then there's nothing to do
        if commission is None or commission == 0.0:
            return None

        # If the quantity is zero (position is no longer held)
        # then the book cost is also zero, so does not need adjusting
        if self.quantity == 0.0:
            return None

        # For simplicity the commission costs are 'shared'
        # across all units in a position
        position_cost = self.book_cost_pu * self.quantity
        final_cost = position_cost + commission
        self.book_cost_pu = final_cost / self.quantity
        self.book_cost = self.book_cost_pu * self.quantity

    def update(self, transaction):
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

        # Sum the position and transaction quantities then
        # adjust book cost depending upon transaction direction
        total_quantity = self.quantity + transaction.quantity
        if total_quantity == 0.0:
            self.book_cost_pu = 0.0
            self.book_cost = 0.0
        else:
            if self.direction == transaction.direction:
                # Increasing a long or short position
                position_cost = self.book_cost_pu * self.quantity
                transaction_cost = transaction.quantity * transaction.price
                total_cost = position_cost + transaction_cost
                self.book_cost_pu = total_cost / total_quantity
            else:
                # Closing a position out or covering a short position
                if abs(transaction.quantity) > abs(self.quantity):
                    # Transaction quantity exceeds position quantity
                    # so a long position is closed and short position
                    # is open, or a short position has been covered
                    # and we've now gone long
                    self.book_cost_pu = transaction.price
                # else:
                #    # TODO: Implement this branch
                #    raise NotImplementedError(
                #        'Opposing direction with transaction less '
                #        'than position quantity '
                #        'is not yet implemented.'
                #    )

        # Update the current trade information
        if (
            self.current_dt is None or transaction.dt > self.current_dt
        ):
            self.current_price = transaction.price
            self.current_dt = transaction.dt

        # Update to the new quantity of units
        self.quantity = total_quantity

        # Handle the commission cost to adjust book cost
        # per unit and total book cost
        self.update_book_cost_for_commission(
            self.asset, transaction.commission
        )

        # Adjust the total book cost and position direction
        self.book_cost = self.book_cost_pu * self.quantity
        self.direction = np.copysign(1, self.quantity)
