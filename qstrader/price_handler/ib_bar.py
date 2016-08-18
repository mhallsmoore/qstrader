import os

import pandas as pd

from ..price_parser import PriceParser
from .base import AbstractBarPriceHandler
from ..event import BarEvent
from qstrader.ib import IBCallback, IBClient
from swigibpy import Contract, TagValueList


class IBBarPriceHandler(AbstractBarPriceHandler):
    """
    TODO nice comments.
    """
    def __init__(self, events_queue, tickers, settings, mode="historic"):
        self.ib_cb = IBCallback()
        self.ib_client = IBClient(self.ib_cb, settings)
        self.tickers = tickers
        self.events_queue = events_queue
        for ticker in tickers:
            # Set up the IB Contract
            contract = Contract()
            contract.exchange = "SMART"
            contract.symbol = ticker
            contract.secType = "STK"
            contract.currency = "USD"

            if mode == "historic":
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

    def stream_next(self):
        """
        Gets the next bit of data sitting on the IBCallback queue,
        create an event from it and place it on the events queue
        """
        # TODO test and get rid of the sleep here
        import time; time.sleep(5);
        event = self.ib_cb.mkt_data_queue.get()
        self.events_queue.put(event)
