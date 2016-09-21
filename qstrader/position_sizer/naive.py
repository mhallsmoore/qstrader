from .base import AbstractPositionSizer


class NaivePositionSizer(AbstractPositionSizer):
    def __init__(self, default_quantity=100):
        self.default_quantity = default_quantity

    def size_order(self, portfolio, initial_order):
        """
        This NaivePositionSizer object follows all
        suggestions from the initial order without
        modification. Useful for testing simpler
        strategies that do not reside in a larger
        risk-managed portfolio.
        """
        return initial_order
