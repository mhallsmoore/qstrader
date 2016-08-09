from swigibpy import EWrapperVerbose, EPosixClientSocket
import time

class IBCallback(EWrapperVerbose):
    def init_error(self):
        setattr(self, "flag_iserror", False)
        setattr(self, "error_msg", "")

    def error(self, id, errorCode, errorString):
        """
        error handling, simple for now
        Here are some typical IB errors
        INFO: 2107, 2106
        WARNING 326 - can't connect as already connected
        CRITICAL: 502, 504 can't connect to TWS.
            200 no security definition found
            162 no trades
        TODO - integrate logging correctly with notifications for critical errors.
        """

        ERRORS_TO_TRIGGER=[201, 103, 502, 504, 509, 200, 162, 420, 2105, 1100, 478, 201, 399]

        if errorCode in ERRORS_TO_TRIGGER:
            errormsg="IB error id %d errorcode %d string %s" %(id, errorCode, errorString)
            print (errormsg)
            setattr(self, "flag_iserror", True)
            setattr(self, "error_msg", True)



class IBClient(object):
    def __init__(self, callback, config):
        gateway = EPosixClientSocket(callback)
        gateway.eConnect(config.IB_HOST, config.IB_PORT, config.IB_CLIENT)

        self.gateway=gateway
        self.cb=callback

    def speaking_clock(self):
        print ("Getting the time... ")

        self.gateway.reqCurrentTime()

        start_time=time.time()

        self.cb.init_error()

        iserror=False

        while not iserror:
            isfinished = hasattr(self.cb, 'data_the_time_now_is')
            if isfinished:
                break

            iserror=self.cb.flag_iserror

            if (time.time() - start_time) > 30:
                not_finished=False

            if iserror:
                not_finished=False

        if iserror:
            print ("Error happened")
            print (self.cb.error_msg)

        return self.cb.data_the_time_now_is
