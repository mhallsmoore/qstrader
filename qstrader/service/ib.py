import sys
import argparse
import datetime
import collections
import inspect
import queue

import logging
import time
import os.path

from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.utils import iswrapper

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


class IBService(EWrapper, EClient):
    """
    The IBService is the primary conduit of data from QStrader to Interactive Brokers.
    This service provides functions to request data, and allows for
    callbacks to be triggered, which populates "data queues" with the response.

    All methods of the EClient are available (i.e. API Requests), as are
    the callbacks for EWrapper (i.e. API responses). It also provides a set of Queues
    which are populated with the responses from EWrapper. Other components in the
    system should use these queues collect the API response data.

    Any module or component that wishes to interact with IB should do so by using
    methods offered in this class. This ensures that the logic required to talk with IB
    is contained within this class exclusively, with the added benefit that we
    can easily create mock instances of the IBService for testing.
    """
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)

        self.historicalDataQueue = queue.Queue()
        self.waitingHistoricalData = []

        # Connect to IB and make the historic data request.
        # self.connect("127.0.0.1", 4001, clientId=0)
        # self.historicalDataRequests_req()
        #
        # while (self.conn.isConnected() or not self.msg_queue.empty()) and len(self.waitingHistoricalData) != 0:
        #     try:
        #         text = self.msg_queue.get(block=True, timeout=0.2)
        #         if len(text) > MAX_MSG_LEN:
        #             self.wrapper.error(NO_VALID_ID, BAD_LENGTH.code(),
        #                 "%s:%d:%s" % (BAD_LENGTH.msg(), len(text), text))
        #             self.disconnect()
        #             break
        #     except queue.Empty:
        #         logging.debug("queue.get: empty")
        #     else:
        #         fields = comm.read_fields(text)
        #         logging.debug("fields %s", fields)
        #         self.decoder.interpret(fields)
        #
        #     # print("conn:%d queue.sz:%d",
        #     #              self.conn.isConnected(),
        #     #              self.msg_queue.qsize())
        #
        # self.disconnect()


    def error(self, reqId:TickerId, errorCode:int, errorString:str):
        super().error(reqId, errorCode, errorString)
        print("Error. Id: " , reqId, " Code: " , errorCode , " Msg: " , errorString)


    """
    Append `reqId` to waitingHistoricalData, then call the super method.
    """
    def reqHistoricalData(self, reqId:TickerId , contract:Contract, endDateTime:str,
                          durationStr:str, barSizeSetting:str, whatToShow:str,
                          useRTH:int, formatDate:int, chartOptions:TagValueList):
        self.waitingHistoricalData.append(reqId)
        print("REQUESTING HISTORIC, WAITING FOR %s" % len(self.waitingHistoricalData))
        super().reqHistoricalData( reqId, contract, endDateTime,
                                  durationStr, barSizeSetting, whatToShow,
                                  useRTH, formatDate, chartOptions)


    """
    Populate the HistoricalData queue.
    """
    def historicalData(self, reqId:TickerId , date:str, open:float, high:float,
                       low:float, close:float, volume:int, barCount:int,
                        WAP:float, hasGaps:int):
        print("RECEIVED HISTORIC DATA")
        self.historicalDataQueue.put((reqId, date, open, high, low, close,
                                        volume, barCount, WAP, hasGaps))

    """
    Remove `reqId` from waitingHistoricalData
    TODO: Will it work with multiple historical requests for same symbol?
    """
    def historicalDataEnd(self, reqId:int, start:str, end:str):
        print("FINISHED FOR %s" % reqId)
        self.waitingHistoricalData.remove(reqId)
