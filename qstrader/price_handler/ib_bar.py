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
    def __init__(self, events_queue, tickers, settings):
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

            self.ib_client.gateway.reqRealTimeBars(
                # TODO first val should be unique
                1, contract, 5, "TRADES", True, TagValueList()
            )

    def stream_next(self):
        pass
        
