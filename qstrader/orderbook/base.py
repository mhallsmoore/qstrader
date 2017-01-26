from abc import ABCMeta, abstractmethod


class AbstractOrderBook(object):
    """
    The AbstractOrderBook abstract class
    to manage orderbook
    """

    __metaclass__ = ABCMeta

    def price(self, volume=0):
        if volume > 0:
            return self.ask(volume)
        elif volume < 0:
            return self.bid(-volume)
        else:  # volume==0
            return self.midpoint(volume)

    def midpoint(self, volume=0):
        return (self.bid(volume) + self.ask(volume)) // 2

    @abstractmethod
    def bid(self, volume=0):
        """
        Return bid price for a given volume
        if no volume is given, highest bid is returned
        """
        raise NotImplementedError("Should implement bid(...)")

    @abstractmethod
    def ask(self, volume=0):
        """
        Return ask price for a given volume
        if no volume is given, lowest ask is returned
        """
        raise NotImplementedError("Should implement ask(...)")

    def spread(self, volume=0):
        """
        Return spread for a given volume
        """
        return self.ask(volume) - self.bid(volume)
