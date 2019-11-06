from abc import ABCMeta, abstractmethod


class AlphaModel(object):
    """
    Abstract interface for an AlphaModel callable.

    A derived-class instance of AlphaModel takes in an Asset
    Universe and an optional DataHandler instance in order
    to generate forecast signals on Assets.

    These signals are used by the PortfolioConstructionModel
    to generate target weights for the portfolio.

    Implementing __call__ produces a dictionary keyed by
    Asset and with a scalar value as the signal.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self, dt):
        raise NotImplementedError(
            "Should implement __call__()"
        )
