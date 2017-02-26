import os
import datetime
import queue
import pandas as pd
from .base import AbstractBarPriceHandler
from ..event import BarEvent

from ..price_parser import PriceParser
from qstrader.service.ib import IBService

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.utils import iswrapper
from ibapi.contract import *
from ibapi.common import *



#types
from ibapi.utils import (current_fn_name, BadMessage)
from ibapi.common import *
from ibapi.order_condition import *
from ibapi.contract import *
from ibapi.order import *
from ibapi.order_state import *
from ibapi.execution import Execution
from ibapi.execution import ExecutionFilter
from ibapi.commission_report import CommissionReport
from ibapi.scanner import ScannerSubscription
from ibapi.ticktype import *

from ibapi.account_summary_tags import *


class IBBarPriceHandler(AbstractBarPriceHandler):
    """
    Designed to feed either live or historic market data bars
    from an Interactive Brokers connection.

    Uses the IBService to make requests and collect data once responses have returned.

    TODO:
        * Historic/Live mode to be set by whether QSTrader is in Backtest or Live mode
        * IBService should be an initialization parameter
        * Ports, etc, connection strings from config
        * Work with live market data
    """
    def __init__(
        self, events_queue, param_tickers, settings, mode="historic",
        hist_end_date = datetime.datetime.now() - datetime.timedelta(days=3),
        hist_duration="5 D", hist_barsize="1 min"
    ):
        self.ib_service = IBService()
        self.ib_service.connect("127.0.0.1",4001,0)
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
        self.bar_stream = queue.Queue()
        self.events_queue = events_queue
        self.mode = mode
        self.continue_backtest = True
        self.hist_end_date = hist_end_date
        self.hist_duration = hist_duration
        self.qst_barsize = self.barsize_lookup[hist_barsize]
        self.ib_barsize = hist_barsize

        # The position of a ticker in this dict is used as its IB ID.
        self.tickers = {} # TODO gross
        self.ticker_lookup = {}

        for ticker in param_tickers:  # TODO gross param_tickers -- combine above?
            self._subscribe_ticker(ticker)

        self._wait_for_hist_population()
        self._merge_sort_ticker_data()

        import pdb; pdb.set_trace()

    def _subscribe_ticker(self, ticker):
        """
        Request ticker data from IB
        """
        if ticker not in self.tickers:
            # Set up an IB ContractS
            contract = Contract()
            contract.exchange = "SMART"
            contract.symbol = ticker
            contract.secType = "STK"
            contract.currency = "AUD"

        if self.mode == "historic":
            ib_ticker_id = len(self.tickers)
            end_time = datetime.datetime.strftime(self.hist_end_date, "%Y%m%d 17:00:00")
            self.ib_service.reqHistoricalData(
                ib_ticker_id, contract, end_time, self.hist_duration, self.ib_barsize,
                "TRADES", True, 2, None)

        # TODO gross
        self.ticker_lookup[len(self.tickers)] = ticker
        self.tickers[ticker] = {}


    def _wait_for_hist_population(self):
        """
        # TODO this *needs* to be an infinite loop running inside the service,
        # with the service launched on a new Thread or Process
        """
        while (self.ib_service.conn.isConnected() or not self.ib_service.msg_queue.empty()) and len(self.ib_service.waitingHistoricalData) != 0:
            try:
                text = self.ib_service.msg_queue.get(block=True, timeout=0.2)
                if len(text) > MAX_MSG_LEN:
                    self.ib_service.wrapper.error(NO_VALID_ID, BAD_LENGTH.code(),
                        "%s:%d:%s" % (BAD_LENGTH.msg(), len(text), text))
                    self.ib_service.disconnect()
                    break
            except queue.Empty:
                print("queue.get: empty")
            else:
                fields = comm.read_fields(text)
                print("fields %s", fields)
                self.ib_service.decoder.interpret(fields)

            print("conn:%d queue.sz:%d",
                         self.ib_service.conn.isConnected(),
                         self.ib_service.msg_queue.qsize())
        self.ib_service.disconnect()


    def _merge_sort_ticker_data(self):
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
        ticker = self.ticker_lookup[mkt_event[0]]
        time = datetime.datetime.fromtimestamp(int(mkt_event[1]))
        barsize = self.qst_barsize
        open_price = PriceParser.parse(mkt_event[2])
        high_price = PriceParser.parse(mkt_event[3])
        low_price = PriceParser.parse(mkt_event[4])
        close_price = PriceParser.parse(mkt_event[5])
        adj_close_price = PriceParser.parse(mkt_event[5]) # TODO redundant?
        volume = mkt_event[6]
        return BarEvent(
            ticker, time, barsize, open_price, high_price,
            low_price, close_price, volume, adj_close_price
        )


    def stream_next(self):
        """
        Create the next BarEvent and place it onto the event queue.
        """
        mkt_event = self.bar_stream.get()
        if self.bar_stream.empty():
            self.continue_backtest = False
        else:
            # Create, store and return the bar event.
            bev = self._create_event(mkt_event);
            self._store_event(bev)
            self.events_queue.put(bev)
