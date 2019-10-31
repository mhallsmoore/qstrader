from abc import ABCMeta, abstractmethod


class Asset(object):
    """
    Generic asset class that stores meta data about a trading asset.
    """

    __metaclass__ = ABCMeta
