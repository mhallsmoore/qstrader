import datetime

from .base import AbstractBarPriceHandler
from qstrader.ib import IBCallback, IBClient
from qstrader.price_parser import PriceParser
from qstrader.event import BarEvent
from swigibpy import Contract, TagValueList


class IBBarPriceHandler(AbstractBarPriceHandler):
    """
    This class largely acts as an interface between qstrader and ib.py.
    ib.py implements all the core functionality of communicating with the IB API.

    Historic data parameters are from https://www.interactivebrokers.com/en/software/api/apiguide/java/reqhistoricaldata.htm.

    This class is limited to streaming the maximum number of concurrent
    tickers available for your IB connection.
    """
    def __init__(
        self, events_queue, tickers, settings, mode="historic",
        hist_end_date=datetime.datetime.now() - datetime.timedelta(days=1), hist_duration="1 D", hist_barsize="5 mins"
    ):
        self.ib_cb = IBCallback()
        self.ib_client = IBClient(self.ib_cb, settings)
        self.tickers = {} # The position of a ticker in this dict is used as it's IB ID. TODO how to handle unsubscribe? TODO probably quite inefficient
        self.ticker_lookup = {}
        self.events_queue = events_queue
        self.mode = mode
        self.continue_backtest = True

        if self.mode == "historic":
            self.hist_end_date = hist_end_date
            self.hist_duration = hist_duration
            self.hist_barsize = hist_barsize

        for ticker in tickers:
            self.subscribe_ticker(ticker)

    def subscribe_ticker(self, ticker):
        if ticker not in self.tickers:
            # Set up the IB Contract
            contract = Contract()
            contract.exchange = "SMART"
            contract.symbol = ticker
            contract.secType = "STK"
            contract.currency = "AUD"

            if self.mode == "historic":
                end_time = datetime.datetime.strftime(self.hist_end_date, "%Y%m%d 17:00:00")
                self.ib_client.gateway.reqHistoricalData(
                    len(self.tickers), contract, end_time, self.hist_duration, self.hist_barsize,
                    "TRADES", True, 2, TagValueList()
                )
            else:
                self.ib_client.gateway.reqRealTimeBars(
                    len(self.tickers), contract, 5, "TRADES", True, TagValueList()
                )

            self.ticker_lookup[len(self.tickers)] = ticker
            self.tickers[ticker] = {}

    def _create_event(self, mkt_event):
        """
        # mkt_event will be a tuple populated according to https://www.interactivebrokers.com/en/software/api/apiguide/java/historicaldata.htm
        """
        ticker = self.ticker_lookup[mkt_event[0]]
        time = datetime.datetime.fromtimestamp(float(mkt_event[1]))
        open_price = PriceParser.parse(mkt_event[2])
        high_price = PriceParser.parse(mkt_event[3])
        low_price = PriceParser.parse(mkt_event[4])
        close_price = PriceParser.parse(mkt_event[5])
        adj_close_price = PriceParser.parse(mkt_event[5])
        volume = mkt_event[6]

        return BarEvent(
            # TODO PERIOD LOOKUP CORRECTLY
            ticker, time, 300, open_price, high_price,
            low_price, close_price, volume, adj_close_price
        )

    def stream_next(self):
        import pdb; pdb.set_trace()
        """
        This class does not place any events onto the events_queue.
        When the IB API sends a market data event to ib.py, ib.py adds the event
        to the events_queue.
        """
        mkt_event = self.ib_cb.mkt_data_queue.get()
        if self.ib_cb.mkt_data_queue.empty() or mkt_event[1].startswith("finished"):
            self.continue_backtest = False
        else:
            # Create the tick event for the queue
            bev = self._create_event(mkt_event)
            # Store event
            self._store_event(bev)
            self.events_queue.put(bev)
