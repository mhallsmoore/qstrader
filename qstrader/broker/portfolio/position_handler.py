from collections import OrderedDict
import inspect

from qstrader.broker.portfolio.position import Position


class PositionHandler(object):
    """
    A class that keeps track of, and updates, the current
    list of Position instances stored in a Portfolio entity.
    """

    def __init__(self):
        """
        Initialise the PositionHandler object to generate
        an ordered dictionary containing the current positions.
        """
        self.positions = OrderedDict()

    def _check_set_position(self, asset):
        """
        Checks if a position exists in the positions list
        and if not creates a new key, and Position instance
        for this particular asset.
        """
        if asset in self.positions:
            position = self.positions[asset]
        else:
            position = Position(asset)
            self.positions[asset] = position
        return position

    def transact_position(self, transaction):
        """
        Execute the transaction and update the appropriate
        position for the transaction's asset accordingly.
        """
        position = self._check_set_position(transaction.asset)
        position.update(transaction)

        # If the position has zero quantity remove it
        if position.quantity == 0.0:
            del self.positions[transaction.asset]

    def update_position(
        self,
        asset,
        quantity=None,
        current_price=None,
        current_dt=None,
        book_cost_pu=None
    ):
        """
        Update the attributes of a particular Position
        via its Asset.
        """
        position = self._check_set_position(asset)

        # Update each position attribute if
        # the parameters aren't None
        frame = inspect.currentframe()
        varvals = inspect.getargvalues(frame)
        for attr in (
            'quantity', 'current_price',
            'current_dt', 'book_cost_pu'
        ):
            if varvals.locals[attr] is not None:
                setattr(position, attr, varvals.locals[attr])

    def update_commission(self, asset, commission):
        """
        Adjust the book cost per unit of the Position
        instance for this particular Asset.
        """
        if asset in self.positions:
            self.positions[asset].update_book_cost_for_commission(
                asset, commission
            )

    def total_non_cash_book_cost(self):
        """
        Calculate the sum of all the Positions' book costs
        excluding cash.
        """
        return sum(
            pos.book_cost
            for asset, pos in self.positions.items()
        )

    def total_book_cost(self):
        """
        Calculate the sum of all the Positions' book cost
        including cash.
        """
        return sum(
            pos.book_cost if not asset.startswith('CASH') else pos.market_value
            for asset, pos in self.positions.items()
        )

    def total_non_cash_market_value(self):
        """
        Calculate the sum of all the positions' market values
        excluding cash.
        """
        return sum(
            0.0 if asset.startswith('CASH') else pos.market_value
            for asset, pos in self.positions.items()
        )

    def total_market_value(self):
        """
        Calculate the sum of all the positions' market values
        including cash.
        """
        return sum(
            pos.market_value
            for asset, pos in self.positions.items()
        )

    def total_non_cash_unrealised_gain(self):
        """
        Calculate the sum of all the positions'
        unrealised gains excluding cash.
        """
        return sum(
            pos.unrealised_gain
            for asset, pos in self.positions.items()
        )

    def total_unrealised_gain(self):
        """
        Calculate the sum of all the positions'
        unrealised gains including cash.
        """
        return sum(
            0.0 if asset.startswith('CASH') else pos.unrealised_gain
            for asset, pos in self.positions.items()
        )

    def total_non_cash_unrealised_percentage_gain(self):
        """
        Calculate the total unrealised percentage gain
        on the positions excluding cash.
        """
        tbc = self.total_non_cash_book_cost()
        if tbc == 0.0:
            return 0.0
        return (self.total_non_cash_market_value() - tbc) / tbc * 100.0

    def total_unrealised_percentage_gain(self):
        """
        Calculate the total unrealised percentage gain
        on the positions including cash.
        """
        tbc = self.total_book_cost()
        if tbc == 0.0:
            return 0.0
        return (self.total_market_value() - tbc) / tbc * 100.0
