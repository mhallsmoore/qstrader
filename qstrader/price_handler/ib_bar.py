import datetime
import pandas as pd
from qstrader.compat import queue
from .base import AbstractBarPriceHandler
from ..event import BarEvent
from ..price_parser import PriceParser


class IBBarPriceHandler(AbstractBarPriceHandler):
    """
    Designed to feed either live or historic market data bars
    from an Interactive Brokers connection.

    Uses the IBService to make requests and collect data once responses have returned.

    `param_contracts` must be a list of IB Contract objects.

    TODO:
        * Historic/Live mode to be set by whether QSTrader is in Backtest or Live mode
        * Work with live market data
        * Raise exceptions if the user enters data that
          IB won't like (i.e. barsize/duration string formats)
        * Decide/discuss approaches to handle IB's simultaneous data feed limit.
    """
    def __init__(
        self, ib_service, events_queue, param_contracts, settings, mode="historic",
        hist_end_date=datetime.datetime.now() - datetime.timedelta(days=3),
        hist_duration="5 D", hist_barsize="1 min"
    ):
        self.ib_service = ib_service
        self.barsize_lookup = {
            "1 sec": 1,
            "5 secs": 5,
            "15 secs": 15,
            "30 secs": 30,
            "1 min": 60,
            "2 mins": 120,
            "3 mins": 180,
            "5 mins": 300,
            "15 mins": 900,
            "30 mins": 1800,
            "1 hour": 3600,
            "8 hours": 28800,
            "1 day": 86400
        }
        self.tickers = {}  # Required to be populated for some parent methods.
        self.bar_stream = queue.Queue()
        self.events_queue = events_queue
        self.mode = mode
        self.continue_backtest = True
        self.hist_end_date = hist_end_date
        self.hist_duration = hist_duration
        self.qst_barsize = self.barsize_lookup[hist_barsize]
        self.ib_barsize = hist_barsize
        # The position of a contract in this dict is used as its IB ID.
        self.contracts = {}  # TODO gross
        self.contract_lookup = {}
        for contract in param_contracts:  # TODO gross param_contracts -- combine above?
            self._subscribe_contract(contract)
        self._wait_for_hist_population()
        self._merge_sort_contract_data()

    def _subscribe_contract(self, contract):
        """
        Request contract data from IB
        """
        # Add ticker symbol, as required by some parent methods
        self.tickers[contract.symbol] = {}
        if self.mode == "historic":
            ib_contract_id = len(self.contracts)
            end_time = datetime.datetime.strftime(self.hist_end_date, "%Y%m%d 17:00:00")
            self.ib_service.reqHistoricalData(
                ib_contract_id, contract, end_time, self.hist_duration, self.ib_barsize,
                "TRADES", True, 2, None)
        # TODO gross
        self.contract_lookup[len(self.contracts)] = contract.symbol
        self.contracts[contract] = {}

    def _wait_for_hist_population(self):
        """
        Blocks until the historical dataset has been populated.
        """
        while len(self.ib_service.waitingHistoricalData) != 0:
            pass

    def _merge_sort_contract_data(self):
        """
        Collects all the equities data from thte IBService, and populates the
        member Queue `self.bar_stream`. This queue is used for the `stream_next()`
        function.
        """
        historicalData = []
        while not self.ib_service.historicalDataQueue.empty():
            historicalData.append(self.ib_service.historicalDataQueue.get())
        historicalData = sorted(historicalData, key=lambda x: x[1])
        for bar_tuple in historicalData:
            self.bar_stream.put(bar_tuple)

    def _create_event(self, mkt_event):
        """
        mkt_event is a tuple created according to the format:
        http:////www.interactivebrokers.com/en/software/api/apiguide/java/historicaldata.htm
        """
        symbol = self.contract_lookup[mkt_event[0]]
        time = pd.Timestamp(int(mkt_event[1]) * 10**9)
        barsize = self.qst_barsize
        open_price = PriceParser.parse(mkt_event[2])
        high_price = PriceParser.parse(mkt_event[3])
        low_price = PriceParser.parse(mkt_event[4])
        close_price = PriceParser.parse(mkt_event[5])
        adj_close_price = PriceParser.parse(mkt_event[5])  # TODO redundant?
        volume = mkt_event[6]
        return BarEvent(
            symbol, time, barsize, open_price, high_price,
            low_price, close_price, volume, adj_close_price
        )

    def stream_next(self):
        """
        Create the next BarEvent and place it onto the event queue.
        """
        try:
            # Create, store and return the bar event.
            mkt_event = self.bar_stream.get(False)
            bev = self._create_event(mkt_event)
            self._store_event(bev)
            self.events_queue.put(bev)
        except queue.Empty:
            self.continue_backtest = False
