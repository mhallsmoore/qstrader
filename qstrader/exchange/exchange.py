from abc import ABCMeta, abstractmethod


class Exchange(object):
    """
    Interface to a trading exchange such as the NYSE or LSE.
    This class family is only required for simulations, rather than
    live or paper trading.

    It exposes methods for obtaining calendar capability
    for trading opening times and market events.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def is_open_at_datetime(self, dt):
        raise NotImplementedError(
            "Should implement is_open_at_datetime()"
        )
