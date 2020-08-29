from collections import OrderedDict

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

    def transact_position(self, transaction):
        """
        Execute the transaction and update the appropriate
        position for the transaction's asset accordingly.
        """
        asset = transaction.asset
        if asset in self.positions:
            self.positions[asset].transact(transaction)
        else:
            position = Position.open_from_transaction(transaction)
            self.positions[asset] = position

        # If the position has zero quantity remove it
        if self.positions[asset].net_quantity == 0:
            del self.positions[asset]

    def total_market_value(self):
        """
        Calculate the sum of all the positions' market values.
        """
        return sum(
            pos.market_value
            for asset, pos in self.positions.items()
        )

    def total_unrealised_pnl(self):
        """
        Calculate the sum of all the positions' unrealised P&Ls.
        """
        return sum(
            pos.unrealised_pnl
            for asset, pos in self.positions.items()
        )

    def total_realised_pnl(self):
        """
        Calculate the sum of all the positions' realised P&Ls.
        """
        return sum(
            pos.realised_pnl
            for asset, pos in self.positions.items()
        )

    def total_pnl(self):
        """
        Calculate the sum of all the positions' P&Ls.
        """
        return sum(
            pos.total_pnl
            for asset, pos in self.positions.items()
        )
