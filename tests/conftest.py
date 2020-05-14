import pytest


class Helpers:
    @staticmethod
    def assert_order_lists_equal(orders_1, orders_2):
        """
        Carries out Order-wise comparison on all Order attributes
        with exception of the generated ID, in order to determine
        if two order lists are equal.

        Parameters
        ----------
        orders_1 : `List[Order]`
            The first order list.
        orders_2 : `List[Order]`
            The second order list.
        """
        for order_1, order_2 in zip(orders_1, orders_2):
            assert order_1._order_attribs_equal(order_2)


@pytest.fixture
def helpers():
    return Helpers
