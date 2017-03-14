import queue
import threading
from ibapi import comm
from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.common import NO_VALID_ID, MAX_MSG_LEN, TickerId, TagValueList
from ibapi.contract import Contract
from ibapi.errors import BAD_LENGTH


class IBService(EWrapper, EClient, threading.Thread):
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

    Several calls must be made to the IBService in order for it to run correctly.
    These should be called from the user's main `trading-session` script.

    An IBService object must be instantiated, immediately followed by the .connect()
    call, immediately followed by the .start() call, which spawns a thread for the run loop.
    When the trading session is complete, the service should be stopped gracefully by
    calling ibservice.stop_event.set() to break the infinite loop, and ibservice.join()
    to wait for the thread to close.
    """
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        threading.Thread.__init__(self, name='IBService')
        self.stop_event = threading.Event()
        # Set up data queues.
        self.realtimeBarQueue = queue.Queue()
        self.historicalDataQueue = queue.Queue()
        self.waitingHistoricalData = []

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        print("Error. Id: ", reqId, " Code: ", errorCode, " Msg: ", errorString)

    """
    Append `reqId` to waitingHistoricalData, then call the super method.
    """
    def reqHistoricalData(self, reqId: TickerId, contract: Contract, endDateTime: str,
                          durationStr: str, barSizeSetting: str, whatToShow: str,
                          useRTH: int, formatDate: int, chartOptions: TagValueList):
        self.waitingHistoricalData.append(reqId)
        super().reqHistoricalData(reqId, contract, endDateTime,
                                  durationStr, barSizeSetting, whatToShow,
                                  useRTH, formatDate, chartOptions)

    """
    Populate the RealTimeBars queue.
    Note that `time` is the start of the bar
    """
    def realtimeBar(self, reqId: TickerId, time:int, open: float, high: float,
                    low: float, close: float, volume: float,
                    wap: float, count: int):
        self.realtimeBarQueue.put((reqId, time, open, high, low, close,
                                  volume, wap, count))

    """
    Populate the HistoricalData queue.
    """
    def historicalData(self, reqId: TickerId, date: str, open: float, high: float,
                       low: float, close: float, volume: int, barCount: int,
                       WAP: float, hasGaps: int):
        self.historicalDataQueue.put((reqId, date, open, high, low, close,
                                     volume, barCount, WAP, hasGaps))

    """
    Remove `reqId` from waitingHistoricalData
    TODO: Will it work with multiple historical requests for same symbol?
    """
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        self.waitingHistoricalData.remove(reqId)

    """
    Overridden from the Threading class. Infinite loop which handles
    message passing from IB to QSTrader. This loop is run in new thread when
    started.
    """
    def run(self):
        while (self.conn.isConnected() or not self.msg_queue.empty()) and not self.stop_event.is_set():
            try:
                text = self.msg_queue.get(block=True, timeout=0.2)
                if len(text) > MAX_MSG_LEN:
                    self.wrapper.error(NO_VALID_ID, BAD_LENGTH.code(),
                                       "%s:%d:%s" % (BAD_LENGTH.msg(), len(text), text))
                    self.disconnect()
                    break
            except queue.Empty:
                pass  # TODO something more appropriate
            else:
                fields = comm.read_fields(text)
                self.decoder.interpret(fields)

        self.disconnect()
