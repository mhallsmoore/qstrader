import logging

from trading_ig import IGStreamService

from qstrader import setup_logging
from .base import AbstractExecutionHandler
from ..event import (FillEvent, EventType)
from ..price_parser import PriceParser

setup_logging


class IGExecutionHandler(AbstractExecutionHandler):
    """
    The execution handler for IG Markets
    executes Market orders at the moment.

    This classes establishes a REST cached IG session and also stream subscription
    to get real time updates and confirm when the order has been filled and the spread/commission
    """
    # TODO Working orders will be implemented in the future

    def __init__(self, events_queue, ig_service, config, compliance=None):
        """
        Initialises the handler, setting the event queue
        as well as accessing the pricing handler and setting a new cached session against IG Markets API.

        Parameters:
        events_queue - The Queue of Event objects.
        price_handler - The price handlers to obtain price details before executing order
        compliance - Compliance object
        config - Configuration object
        """
        self.events_queue = events_queue
        self.fill_event = None
        self.ig_service = ig_service
        self.compliance = compliance
        self.config = config
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.ig_stream_service, self.ig_stream_session = self._create_streaming_session(ig_service)

    def _create_streaming_session(self, ig_service):

        # Cretes Streaming service and session
        ig_stream_service = IGStreamService(ig_service)
        ig_stream_session = ig_stream_service.create_session()

        return ig_stream_service, ig_stream_session

    def _create_fill_event(self, executed_order):
        executed_order["dealReference"]
        epic = executed_order["epic"]
        # ticker = epic[5:8]
        exchange = epic[1:4]
        action = executed_order["direction"]
        quantity = executed_order["size"]
        fill_price = PriceParser.parse(executed_order["level"]) / 10000
        timestamp = executed_order["date"]
        commission = self.calculate_ig_commission(quantity, fill_price)
        self.logger.info("Created filled event")
        self.logger.debug('Data received: %s' % executed_order)
        self.fill_event = FillEvent(timestamp, epic, action, quantity, exchange, fill_price, commission)
        self.events_queue.put(self.fill_event)

    def calculate_ig_commission(self, quantity, fill_price):
        """
        Calculate the IG Markets commission for
        a transaction.
        """
        # TODO implement logic if required (IG Market doesn't have commission as it is included in spread)
        commission = 0
        return PriceParser.parse(commission)

    def execute_order(self, event):
        """
        Executes Market orders directly, OrderEvents into FillEvents through IG Markets API,
        this means it has to track the order synchronously and return confirmation

        Parameters:
        event - An Event object with order information.
        """

        if event.type == EventType.ORDER:
            # Obtain values from the OrderEvent
            ticker = event.ticker
            # Mapping original IB order action to IG terminology
            if event.action == "BOT":
                action = "BUY"
            else:
                action = "SELL"
            quantity = event.quantity

            # Execute Market order
            executed_order = self.ig_service.create_open_position("GBP",
                                                                  action,
                                                                  ticker,
                                                                  # str(datetime.now() + timedelta(hours=3)),
                                                                  "DFB",
                                                                  False,
                                                                  False,
                                                                  None,
                                                                  None,
                                                                  None,
                                                                  "MARKET",
                                                                  None,
                                                                  quantity,
                                                                  None,
                                                                  None
                                                                  )

            # Track confirmation from IG and update fill price with
            if executed_order["dealStatus"] == "ACCEPTED":
                self._create_fill_event(executed_order)
                if self.compliance is not None:
                    self.compliance.record_trade(self.fill_event)
            else:
                self.logger.error('Order execution failed, reason: %s, quantity: %s, ticker: %s' % (executed_order["reason"], quantity, ticker))

            return executed_order
