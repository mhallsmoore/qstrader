from abc import ABCMeta, abstractmethod


class OrderSizeGeneration(object):
    """
    Creates a target portfolio of quantities for each Asset
    using its provided weight and total equity available in the Broker portfolio.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self, dt, weights):
        raise NotImplementedError(
            "Should implement call()"
        )
