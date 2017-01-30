from .base import AbstractOrderBook
from .exceptions import OrderBookConstructionException, OrderBookLiquidityException


def issorted(lst, reverse=False):
    return sorted(lst, reverse=reverse) == lst


def isunique(lst):
    s = set()
    for lv in lst:
        s.add(lv.price)
    return len(s) == len(lst)


class FiniteDepthOrderBook(AbstractOrderBook):
    def __init__(self, asks, bids):
        if not issorted(asks):
            raise OrderBookConstructionException("asks must have price ascending")

        if not issorted(bids, reverse=True):
            raise OrderBookConstructionException("bids must have price descending")

        if not isunique(bids):
            raise OrderBookConstructionException("bids must have unique prices")

        if not isunique(asks):
            raise OrderBookConstructionException("asks must have unique prices")

        self._asks = asks
        self._bids = bids

    def _price(self, v_level, volume):
        assert volume >= 0, "volume must be positive or zero"
        remaining_volume = volume
        price_volume_sum = 0
        for level in v_level:
            if level.volume >= remaining_volume:
                taken_volume = remaining_volume
                remaining_volume = 0
                price_volume_sum += (level.price * taken_volume)
                break
            else:
                taken_volume = level.volume
                remaining_volume -= level.volume
                price_volume_sum += (level.price * level.volume)
        total_volume = volume - remaining_volume
        price = price_volume_sum / total_volume
        if remaining_volume != 0:
            raise OrderBookLiquidityException("Orderbook doesn't have enough depth")
        return price

    def bid(self, volume=0):
        if volume == 0:
            return self._bids[0].price
        else:
            return self._price(self._bids, volume)

    def ask(self, volume=0):
        if volume == 0:
            return self._asks[0].price
        else:
            return self._price(self._asks, volume)
