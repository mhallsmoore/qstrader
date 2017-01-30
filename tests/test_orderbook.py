import unittest

from qstrader.orderbook import InfiniteDepthOrderBook, FiniteDepthOrderBook
from qstrader.orderbook.exceptions import OrderBookConstructionException, OrderBookLiquidityException
from qstrader.orderbook.level import Level


class TestInfiniteDepthOrderBook(unittest.TestCase):
    """
    Test an orderbook with infinite depth
    """
    def setUp(self):
        pass

    def test_orderbook_with_bid_ask(self):
        _ask, _bid = 110.0, 100.0
        self.ob = InfiniteDepthOrderBook(_ask, _bid)

        self.assertEqual(self.ob.spread(), 10.0)
        self.assertEqual(self.ob.bid(), 100.0)
        self.assertEqual(self.ob.ask(), 110.0)
        volume = 50
        self.assertEqual(self.ob.bid(volume), 100.0)
        self.assertEqual(self.ob.ask(volume), 110.0)

    def test_orderbook_with_only_one_price(self):
        price = 100.0
        self.ob = InfiniteDepthOrderBook(price)
        self.assertEqual(self.ob.bid(), price)
        self.assertEqual(self.ob.ask(), price)
        self.assertEqual(self.ob.spread(), 0.0)
        volume = 50
        self.assertEqual(self.ob.bid(volume), price)
        self.assertEqual(self.ob.ask(volume), price)
        self.assertEqual(self.ob.spread(volume), 0.0)

    def test_orderbook_construction_error(self):
        _ask, _bid = 100.0, 110.0  # NOT ask >= bid
        self.assertRaises(OrderBookConstructionException, InfiniteDepthOrderBook, _ask, _bid)

    def test_illiquid_orderbook(self):
        _ask, _bid = 110.0, 100.0
        _vol = 100
        self.ob = InfiniteDepthOrderBook(_ask, _bid, _vol)
        self.assertRaises(OrderBookLiquidityException, self.ob.price, _vol + 10)


class TestLevel(unittest.TestCase):
    def test_level(self):
        l1 = Level(1.34, 100.2)
        l2 = Level(1.35, 110.2)
        self.assertTrue(l1 < l2)


class TestFiniteDepthOrderBook(unittest.TestCase):
    """
    Test an orderbook with finite depth
    """
    def setUp(self):
        pass

    def test_low_volume(self):
        asks = [Level(110.0, 10.0), Level(111.0, 12.0)]  # asks (ascending asks)
        bids = [Level(100.0, 10.0), Level(99.0, 15.0)]  # bids (descending prices)

        ob = FiniteDepthOrderBook(asks, bids)
        self.assertEqual(ob.bid(), 100.0)
        self.assertEqual(ob.ask(), 110.0)
        self.assertEqual(ob.spread(), 10.0)

        volume = 15
        expected_bid = (100.0 * 10.0 + 99.0 * 5.0) / 15.0
        calc_bid = ob.bid(volume)
        self.assertEqual(calc_bid, expected_bid)

        expected_ask = (110.0 * 10.0 + 111 * 5.0) / 15.0
        calc_ask = ob.ask(volume)
        self.assertEqual(calc_ask, expected_ask)

        self.assertEqual(ob.spread(volume), expected_ask - expected_bid)

        self.assertEqual(ob.price(volume), ob.ask(volume))
        self.assertEqual(ob.price(-volume), ob.bid(volume))

    def test_illiquid_orderbook(self):
        asks = [Level(110.0, 10.0), Level(111.0, 12.0)]  # asks (ascending asks)
        bids = [Level(100.0, 10.0), Level(99.0, 15.0)]  # bids (descending prices)

        ob = FiniteDepthOrderBook(asks, bids)

        volume = 50.0
        self.assertRaises(OrderBookLiquidityException, ob.spread, volume)

    def test_construction_error_not_ascending_asks(self):
        asks = [Level(111.0, 10.0), Level(110.0, 12.0)]  # asks (NOT ascending asks)
        bids = [Level(100.0, 10.0), Level(99.0, 15.0)]  # bids (descending prices)
        self.assertRaises(OrderBookConstructionException, FiniteDepthOrderBook, asks, bids)

    def test_construction_error_not_descending_bids(self):
        asks = [Level(110.0, 10.0), Level(111.0, 12.0)]  # asks (ascending asks)
        bids = [Level(99.0, 10.0), Level(100.0, 15.0)]  # bids (NOT descending prices)
        self.assertRaises(OrderBookConstructionException, FiniteDepthOrderBook, asks, bids)

    def test_construction_error_not_unique_asks(self):
        asks = [Level(111.0, 10.0), Level(111.0, 12.0)]  # asks (NOT unique prices)
        bids = [Level(100.0, 10.0), Level(99.0, 15.0)]  # bids (descending prices)
        self.assertRaises(OrderBookConstructionException, FiniteDepthOrderBook, asks, bids)

    def test_construction_error_not_unique_bids(self):
        asks = [Level(110.0, 10.0), Level(111.0, 12.0)]  # asks (ascending asks)
        bids = [Level(100.0, 10.0), Level(100.0, 15.0)]  # bids (NOT unique prices)
        self.assertRaises(OrderBookConstructionException, FiniteDepthOrderBook, asks, bids)
