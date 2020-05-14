from abc import ABCMeta, abstractmethod


class ExecutionAlgorithm(object):
    """
    Callable which takes in a list of desired rebalance Orders
    and outputs a new Order list with a particular execution
    algorithm strategy.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self, dt, initial_orders):
        raise NotImplementedError(
            "Should implement __call__()"
        )
