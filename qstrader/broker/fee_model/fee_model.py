from abc import ABCMeta, abstractmethod


class FeeModel(object):
    """
    Abstract class to handle the calculation of brokerage
    commission, fees and taxes.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def _calc_commission(self, asset, quantity, consideration, broker=None):
        raise NotImplementedError(
            "Should implement _calc_commission()"
        )

    @abstractmethod
    def _calc_tax(self, asset, quantity, consideration, broker=None):
        raise NotImplementedError(
            "Should implement _calc_tax()"
        )

    @abstractmethod
    def calc_total_cost(self, asset, quantity, consideration, broker=None):
        raise NotImplementedError(
            "Should implement calc_total_cost()"
        )
