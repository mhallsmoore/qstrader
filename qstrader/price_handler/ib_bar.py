from .base import AbstractBarPriceHandler
from qstrader.ib import IBCallback, IBClient
from swigibpy import Contract, TagValueList


class IBBarPriceHandler(AbstractBarPriceHandler):
    """
    This class largely acts as an interface between qstrader and ib.py.
    ib.py implements all the core functionality of communicating with the IB API.

    This class is limited to streaming the maximum number of concurrent
    tickers available for your IB connection.
    """
    def __init__(self, events_queue, tickers, settings, mode="historic"):
        self.ib_cb = IBCallback(mkt_data_queue=events_queue)
        self.ib_client = IBClient(self.ib_cb, settings)
        self.tickers = []
        self.events_queue = events_queue
        self.mode = mode
        self.continue_backtest = True
        for ticker in tickers:
            self.subscribe_ticker(ticker)

    def subscribe_ticker(self, ticker):
        if ticker not in self.tickers:
            # Set up the IB Contract
            contract = Contract()
            contract.exchange = "SMART"
            contract.symbol = ticker
            contract.secType = "STK"
            contract.currency = "USD"

            if self.mode == "historic":
                self.ib_client.gateway.reqHistoricalData(
                    # TODO first val should be unique
                    1, contract, "20160818 17:30:30", "1 D", "5 mins", "TRADES",
                    True, 2, TagValueList()
                )
            else:
                self.ib_client.gateway.reqRealTimeBars(
                    # TODO first val should be unique
                    1, contract, 5, "TRADES", True, TagValueList()
                )
            self.tickers.append(ticker)

    def stream_next(self):
        """
        This class does not place any events onto the events_queue.
        When the IB API sends a market data event to ib.py, ib.py adds the event
        to the events_queue.

        TODO - stop backtest when we receive a 'finished' event from IB?
        """
        if self.events_queue.empty():
            self.continue_backtest = False
