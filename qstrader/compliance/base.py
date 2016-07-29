from abc import ABCMeta, abstractmethod


class AbstractCompliance(object):
    """
    The Compliance component should be given every trade
    that occurs in qstrader.

    It is designed to keep track of anything that may
    be required for regulatory or audit (or debugging)
    purposes. Extended versions can write trades to a
    CSV, or a database.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def record_trade(self, fill):
        """
        Takes a FillEvent from an ExecutionHandler
        and logs each of these.

        Parameters:
        fill - A FillEvent with information about the
        trade that has just been executed.
        """
        raise NotImplementedError("Should implement record_trade()")
