import logging
import traceback

import pandas as pd
from trading_ig import IGStreamService
from trading_ig.lightstreamer import Subscription

from qstrader import setup_logging
from .base import AbstractTickPriceHandler
from ..event import TickEvent
from ..price_parser import PriceParser

setup_logging


class IGTickPriceHandler(AbstractTickPriceHandler):
    def __init__(self, events_queue, ig_service, tickers, config):
        self.price_event = None
        self.events_queue = events_queue
        self.ig_stream_service, self.ig_stream_session = self._create_streaming_session(ig_service, accountId=config.IG_ACC_ID)
        self.tickers_lst = tickers
        self.tickers_subs = ["MARKET:" + ticker for ticker in tickers]
        self.tickers = {}
        for ticker in self.tickers_lst:
            self.tickers[ticker] = {}
        # Set up logging
        self.logger = logging.getLogger(__name__)

    def subscribe(self):
        # Making a new Subscription in MERGE mode
        subcription_prices = Subscription(
            mode="MERGE",
            items=self.tickers_subs,
            fields=["BID", "OFFER", "CHANGE", "MARKET_STATE", "UPDATE_TIME"],
            # adapter="QUOTE_ADAPTER"
        )

        # Adding the "on_price_update" function to Subscription
        subcription_prices.addlistener(self._on_prices_update)

        # Registering the Subscription
        self.logger.info("Registering the Subscription")
        try:
            self.ig_stream_service.ls_client.subscribe(subcription_prices)
        except Exception:
            self.logger.error("Error while subscribing")
            print(traceback.format_exc())

    def _create_streaming_session(self, ig_service, accountId):

        # Cretes Streaming service and session
        ig_stream_service = IGStreamService(ig_service)
        ig_stream_session = ig_stream_service.create_session()

        # Connect with specified Listener
        ig_stream_service.connect(accountId)

        return ig_stream_service, ig_stream_session

    def _on_prices_update(self, data):
        if data["values"]["MARKET_STATE"] == "TRADEABLE":
            tick_event = self._create_event(data)
            if tick_event is not None:
                self.logger.debug("Price update received")
                self.logger.debug('Data received: %s' % data)
                self.logger.debug("Storing price update as instrument is tradeable")
                self._store_price_event(tick_event)
        else:
            self.logger.info("Event not stored as market is closed/instrument is not tradeable")

    def _create_event(self, data):
        ticker = data["name"][7:]
        index = pd.to_datetime(data["values"]["UPDATE_TIME"])
        bid = PriceParser.parse(data["values"]["BID"]) / 10000
        ask = PriceParser.parse(data["values"]["OFFER"]) / 10000
        return TickEvent(ticker, index, bid, ask)

    def _store_price_event(self, tick_event):
        """
        Place the next PriceEvent (BarEvent or TickEvent) onto the event queue.
        """
        if tick_event is not None:
            self._store_event(tick_event)
            self.events_queue.put(tick_event)
