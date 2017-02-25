import os
import datetime
import queue
from .base import AbstractBarPriceHandler

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
    """
    def __init__(
        self, events_queue, param_tickers, settings, mode="historic",
        hist_end_date = datetime.datetime.now() - datetime.timedelta(days=3),
        hist_duration="5 D", hist_barsize="1 min"
    ):
        self.ib_service = IBService()
        self.ib_service.connect("127.0.0.1",4001,0)
        self.mode = mode
        self.continue_backtest = True
        self.hist_end_date = hist_end_date
        self.hist_duration = hist_duration
        self.hist_barsize = hist_barsize

        # The position of a ticker in this dict is used as its IB ID.
        self.tickers = {} # TODO gross
        self.ticker_lookup = {}

        for ticker in param_tickers:  # TODO gross param_tickers -- combine above?
            self._subscribe_ticker(ticker)

        self._wait_for_hist_population()


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
                ib_ticker_id, contract, end_time, self.hist_duration, self.hist_barsize,
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
