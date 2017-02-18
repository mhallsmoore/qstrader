import os
import datetime
from .base import AbstractBarPriceHandler

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import *

import logging

class IBClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)


class IBWrapper(EWrapper):
    def __init__(self):
        EWrapper.__init__(self)

    def historicalData(self, reqId:int, date:str, open:float, high:float,
                        low: float, close:float, volume: int, barCount: int,
                        WAP:float, hasGaps: int):
        logging.error("RECEIVED HISTORICAL DATA BAR.")


class IBBarPriceHandler(AbstractBarPriceHandler, IBWrapper, IBClient):
    """
    Designed to feed either live or historic market data bars
    from an Interactive Brokers connection.

    Each "IB-connected" module requires its 'client' and 'wrapper' methods.

    TODO:
        * Historic/Live mode to be set by whether QSTrader is in Backtest or Live mode
    """
    def __init__(
        self, events_queue, tickers, settings, mode="historic",
        hist_end_date = datetime.datetime.now() - datetime.timedelta(days=3),
        hist_duration="1 D", hist_barsize="1 min"
    ):
        logging.basicConfig( level=logging.ERROR )

        self.ib_wrapper = IBWrapper()
        self.ib_client = IBClient(self.ib_wrapper)

        self.ib_client.connect("127.0.0.1",4001,0)

        self.tickers = {}
        self.mode = mode
        self.continue_backtest = True
        self.hist_end_date = hist_end_date
        self.hist_duration = hist_duration
        self.hist_barsize = hist_barsize

        for ticker in tickers:
            self._subscribe_ticker(ticker)

        import time
        time.sleep(10)


    def _subscribe_ticker(self, ticker):
        if ticker not in self.tickers:
            # Set up an IB ContractS
            contract = Contract()
            contract.exchange = "SMART"
            contract.symbol = ticker
            contract.secType = "STK"
            contract.currency = "USD"

        if self.mode == "historic":
            end_time = datetime.datetime.strftime(self.hist_end_date, "%Y%m%d 17:00:00")
            self.ib_client.reqHistoricalData(
                0, contract, end_time, self.hist_duration, self.hist_barsize,
                "TRADES", True, 2, None)
