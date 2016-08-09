import pandas as pd

from trading_ig.lightstreamer import Subscription

from ..price_parser import PriceParser
from ..event import TickEvent
from .base import AbstractTickPriceHandler


class IGTickPriceHandler(AbstractTickPriceHandler):
    def __init__(self, events_queue, ig_stream_service, tickers):
        self.price_event = None
        self.events_queue = events_queue
        self.continue_backtest = True
        self.ig_stream_service = ig_stream_service
        self.tickers_lst = tickers
        self.tickers = {}
        for ticker in self.tickers_lst:
            self.tickers[ticker] = {}

        # Making a new Subscription in MERGE mode
        subcription_prices = Subscription(
            mode="MERGE",
            items=tickers,
            fields=["UPDATE_TIME", "BID", "OFFER", "CHANGE", "MARKET_STATE"],
            # adapter="QUOTE_ADAPTER",
        )

        # Adding the "on_price_update" function to Subscription
        subcription_prices.addlistener(self.on_prices_update)

        # Registering the Subscription
        self.ig_stream_service.ls_client.subscribe(subcription_prices)

    def on_prices_update(self, data):
        tev = self._create_event(data)
        if self.price_event is not None:
            print("losing %s" % self.price_event)
        self.price_event = tev

    def _create_event(self, data):
        ticker = data["name"]
        index = pd.to_datetime(data["values"]["UPDATE_TIME"])
        bid = PriceParser.parse(data["values"]["BID"])
        ask = PriceParser.parse(data["values"]["OFFER"])
        return TickEvent(ticker, index, bid, ask)

    def stream_next(self):
        """
        Place the next PriceEvent (BarEvent or TickEvent) onto the event queue.
        """
        if self.price_event is not None:
            self._store_event(self.price_event)
            self.events_queue.put(self.price_event)
            self.price_event = None
