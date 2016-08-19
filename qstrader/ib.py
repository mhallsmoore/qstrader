import sys
from swigibpy import EWrapper, EPosixClientSocket
from qstrader.event import BarEvent


class IBClientError(Exception):
    pass


class IBError(Exception):
    pass


class IBSystemError(Exception):
    pass


class IBCallback(EWrapper):
    # Create a multiprocess queue for us to store data that comes in.
    def __init__(self, mkt_data_queue=None):
        super(IBCallback, self).__init__()
        if mkt_data_queue is not None:
            self.mkt_data_queue = mkt_data_queue

    # Raise exceptions for any errors which occur.
    def error(self, id, errorCode, errorString):
        """TODO - Log info/warnings/exceptions correctly."""
        if errorCode == 165:  # Historical data sevice message
            sys.stderr.write("TWS INFO - %s: %s\n" % (errorCode, errorString))

        elif errorCode >= 501 and errorCode < 600:  # Socket read failed
            raise IBClientError("IB CLIENT-ERROR - %s: %s\n" % (errorCode, errorString))

        elif errorCode >= 100 and errorCode < 1100:
            raise IBError("IB ERROR - %s: %s\n" % (errorCode, errorString))

        elif errorCode >= 1100 and errorCode < 2100:
            raise IBSystemError("IB SYSTEM-ERROR - %s: %s\n" % (errorCode, errorString))

        elif errorCode in (2104, 2106, 2108):
            sys.stderr.write("TWS INFO - %s: %s\n" % (errorCode, errorString))

        elif errorCode >= 2100 and errorCode <= 2110:
            sys.stderr.write("TWS WARNING - %s: %s\n" % (errorCode, errorString))

        else:
            sys.stderr.write("TWS ERROR - %s: %s\n" % (errorCode, errorString))

    # Swigibpy defaults to printing exception. Raise it instead.
    def pyError(self, exception, value, traceback):
        print("EXCEPTION: %s" % value)
        raise exception(value)

    # Implementation required
    def managedAccounts(self, message):
        print("IBCallback.managedAccounts: %s" % message)

    # Implementation required
    def nextValidId(self, orderId):
        print("IBCallback.nextValidId: %s" % orderId)

    def historicalData(
        self, reqId, date, open_price,
        high_price, low_price, close_price,
        volume, count, WAP, hasGaps
    ):
        # TODO get ticker from reqId
        # TODO get proper period of bar
        # TODO turn data into integers
        event = BarEvent(
            reqId, date, 300, open_price,
            high_price, low_price, close_price, volume
        )
        self.mkt_data_queue.put(event)


class IBClient(object):
    def __init__(self, callback, config):
        gateway = EPosixClientSocket(callback)
        gateway.eConnect(config.IB_HOST, config.IB_PORT, config.IB_CLIENT)

        self.gateway = gateway
        self.cb = callback
