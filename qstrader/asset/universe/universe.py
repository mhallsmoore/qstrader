from abc import ABCMeta, abstractmethod


class Universe(object):
    """
    Interface specification for an Asset Universe.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_assets(self, dt):
        raise NotImplementedError(
            "Should implement get_assets()"
        )
