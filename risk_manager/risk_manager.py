from qstrader.event.event import OrderEvent


class TestRiskManager(object):
    def __init__(self):
        pass

    def refine_orders(self, portfolio, sized_order):
        """
        This TestRiskManager object simply lets the
        sized order through, creates the corresponding
        OrderEvent object and adds it to a list.
        """
        order_event = OrderEvent(
            sized_order.ticker,
            sized_order.action,
            sized_order.quantity
        )
        return [order_event]