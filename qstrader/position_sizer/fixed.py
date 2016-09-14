from .base import AbstractPositionSizer


class FixedPositionSizer(AbstractPositionSizer):
    def __init__(self, default_quantity=100):
        self.default_quantity = default_quantity

    def size_order(self, portfolio, initial_order):
        """
        This FixedPositionSizer object simply modifies
        the quantity to be 100 of any share transacted.
        """
        initial_order.quantity = self.default_quantity
        return initial_order
