from decimal import Decimal

from .base import AbstractExecutionHandler
from ..event import (FillEvent, EventType)

try:
    from qstrader import settings
except ImportError:
    print(
        "Could not import settings.py. Have you copied " \
        "settings.py.example to settings.py and configured " \
        "your QSTrader settings?"
    )


class IBSimulatedExecutionHandler(AbstractExecutionHandler):
    """
    The simulated execution handler for Interactive Brokers
    converts all order objects into their equivalent fill
    objects automatically without latency, slippage or
    fill-ratio issues.

    This allows a straightforward "first go" test of any strategy,
    before implementation with a more sophisticated execution
    handler.
    """

    def __init__(self, events_queue, price_handler, compliance=None):
        """
        Initialises the handler, setting the event queue
        as well as access to local pricing.

        Parameters:
        events_queue - The Queue of Event objects.
        """
        self.events_queue = events_queue
        self.price_handler = price_handler
        self.compliance = compliance

    def calculate_ib_commission(self):
        """
        Calculate the Interactive Brokers commission for
        a transaction. At this stage, simply add in $1.00
        for transaction costs, irrespective of lot size.
        """
        return 1 * settings.PRICE_MULTIPLIER

    def execute_order(self, event):
        """
        Converts OrderEvents into FillEvents "naively",
        i.e. without any latency, slippage or fill ratio problems.

        Parameters:
        event - An Event object with order information.
        """
        if event.type == EventType.ORDER:
            # Obtain values from the OrderEvent
            timestamp = self.price_handler.get_last_timestamp(event.ticker)
            ticker = event.ticker
            action = event.action
            quantity = event.quantity

            # Obtain the fill price
            if self.price_handler.istick():
                bid, ask = self.price_handler.get_best_bid_ask(ticker)
                if event.action == "BOT":
                    fill_price = ask
                else:
                    fill_price = bid
            else:
                close_price = self.price_handler.get_last_close(ticker)
                fill_price = close_price

            # Set a dummy exchange and calculate trade commission
            exchange = "ARCA"
            commission = self.calculate_ib_commission()

            # Create the FillEvent and place on the events queue
            fill_event = FillEvent(
                timestamp, ticker,
                action, quantity,
                exchange, fill_price,
                commission
            )
            self.events_queue.put(fill_event)

            if self.compliance is not None:
                self.compliance.record_trade(fill_event)
