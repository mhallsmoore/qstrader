import sys
from swigibpy import EWrapper, EPosixClientSocket


class IBClientError(Exception):
    pass


class IBError(Exception):
    pass


class IBSystemError(Exception):
    pass


class IBCallback(EWrapper):

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
        raise exception(value)


class IBClient(object):
    def __init__(self, callback, config):
        gateway = EPosixClientSocket(callback)
        gateway.eConnect(config.IB_HOST, config.IB_PORT, config.IB_CLIENT)

        self.gateway = gateway
        self.cb = callback

    def speaking_clock(self):
        pass
        # print ("Getting the time... ")
        #
        # self.gateway.reqCurrentTime()
        #
        # start_time=time.time()
        #
        # self.cb.init_error()
        #
        # iserror=False
        #
        # while not iserror:
        #     isfinished = hasattr(self.cb, 'data_the_time_now_is')
        #     if isfinished:
        #         break
        #
        #     iserror=self.cb.flag_iserror
        #
        #     if (time.time() - start_time) > 30:
        #         not_finished=False
        #
        #     if iserror:
        #         not_finished=False
        #
        # if iserror:
        #     print ("Error happened")
        #     print (self.cb.error_msg)
        #
        # return self.cb.data_the_time_now_is
