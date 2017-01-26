from .base import AbstractOrderBook
from .exceptions import OrderBookConstructionException, OrderBookLiquidityException


class InfiniteDepthOrderBook(AbstractOrderBook):
    def __init__(self, lowest_ask, highest_bid=None, volume=None):
        if highest_bid is None:
            highest_bid = lowest_ask
        if lowest_ask < highest_bid:
            raise OrderBookConstructionException("lowest_ask must be greater than or equal to highest_bid")

        self._highest_bid = highest_bid
        self._lowest_ask = lowest_ask
        self._volume = volume  # maximum volume

    def _test_liquidity(self, volume):
        if self._volume is not None:
            if volume > self._volume:
                raise OrderBookLiquidityException("illiquid orderbook")

    def bid(self, volume=0):
        """
        Return highest bid
        """
        self._test_liquidity(volume)
        return self._highest_bid

    def ask(self, volume=0):
        """
        Return lowest ask
        """
        self._test_liquidity(volume)
        return self._lowest_ask
