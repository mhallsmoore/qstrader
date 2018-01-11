import unittest
import numpy as np
import pandas as pd
from qstrader.price_parser import PriceParser
from qstrader.price_handler.ib_bar import IBBarPriceHandler
from qstrader.compat import queue
from qstrader import settings
from ibapi.contract import Contract

"""
TODO
    * Code repetition in this file
    * Swaps between camelCase and snake_case,
      largely because IB uses camelCase. Be more consistent?
    * Test that the price handler called IBService methods with correct params.
"""


# Starting at 2017-01-01 13:00:00, 1 minute bars.
timestamp = 1483275600
closes = np.arange(80.00, 91.00, 1)


class IBServiceMock(object):
    def __init__(self):
        self.historicalDataQueue = queue.Queue()
        self.realtimeBarQueue = queue.Queue()
        self.waitingHistoricalData = []
        self.countHistoricalRequestsMade = 0
        self.countMarketDataRequestsMade = 0
        # Populate some historic data for the mock service.
        # CBA mock data
        for i in range(0, 10):
            self.historicalDataQueue.put((0, timestamp + (i * 60),
                                         closes[i], closes[i] + 1,
                                         closes[i] - 1, closes[i + 1],
                                         1000000, 100, closes[i], False))
        # BHP mock data
        for i in range(0, 10):
            self.historicalDataQueue.put((1, timestamp + (i * 60),
                                         closes[i] / 2, closes[i] + 1 / 2,
                                         (closes[i] - 1) / 2, closes[i + 1] / 2,
                                         1000000, 100, closes[i] / 2, False))

        # Populate mock realtimeBars
        for i in range(0, 10):
            # CBA
            self.realtimeBarQueue.put((0, timestamp + (i * 60),
                                      closes[i], closes[i] + 1,
                                      closes[i] - 1, closes[i + 1],
                                      1000000, 100, closes[i], False))
            # BHP
            self.realtimeBarQueue.put((1, timestamp + (i * 60),
                                      closes[i] / 2, closes[i] + 1 / 2,
                                      (closes[i] - 1) / 2, closes[i + 1] / 2,
                                      1000000, 100, closes[i] / 2, False))

    def reqHistoricalData(self, *arg):
        self.countHistoricalRequestsMade += 1

    def reqRealTimeBars(self, *arg):
        self.countMarketDataRequestsMade += 1


class TestPriceHandlerLiveCase(unittest.TestCase):
    def setUp(self):
        """
        Set up the PriceHandler object with a small
        set of market data for a mocked 'live' trading session.

        TODO:
            * Test multiple timeframes
            * Test successfully cancels market data feeds
            * Test handling of maxing out IB's market data streaming connections
            * Test that live can understand 'start' of a bar, but historic
              might use 'end' of a bar (RE timestamps)??
        """
        self.ib_service = IBServiceMock()
        self.config = settings.TEST
        events_queue = queue.Queue()

        # Set up an IB Contract for CBA and BHP
        cba = Contract()
        cba.exchange = "SMART"
        cba.symbol = "CBA"
        cba.secType = "STK"
        cba.currency = "AUD"

        bhp = Contract()
        bhp.exchange = "SMART"
        bhp.symbol = "BHP"
        bhp.secType = "STK"
        bhp.currency = "AUD"

        # Create the price handler.
        self.price_handler = IBBarPriceHandler(
            self.ib_service, events_queue, [cba, bhp], self.config, mode="live"
        )

    def test_stream_all_live_events(self):
        """
        Will test that:
            * live data is requested and collected from IBService
            * live data is streamed out correctly
        """
        for i in range(0, 10):
            # Test CBA
            self.price_handler.stream_next()
            self.assertEqual(
                self.price_handler.tickers["CBA"]["timestamp"],
                pd.Timestamp((timestamp + (i * 60)) * 1e9)
            )
            self.assertEqual(
                PriceParser.display(self.price_handler.tickers["CBA"]["close"]),
                closes[i + 1]  # Close is next open
            )

            # Test BHP
            self.price_handler.stream_next()
            self.assertEqual(
                self.price_handler.tickers["BHP"]["timestamp"],
                pd.Timestamp((timestamp + (i * 60)) * 1e9)
            )
            self.assertEqual(
                PriceParser.display(self.price_handler.tickers["BHP"]["close"]),
                closes[i + 1] / 2  # Close is next open
            )

    def test_made_market_data_requests(self):
        self.assertEqual(self.ib_service.countMarketDataRequestsMade, 2)


class TestPriceHandlerHistoricCase(unittest.TestCase):
    def setUp(self):
        """
        Set up the PriceHandler object with a small
        set of initial tickers for a backtest in historic mode.

        TODO:
            * Test multiple timeframes
            * Test mocked live market data methods
        """
        self.ib_service = IBServiceMock()
        self.config = settings.TEST
        events_queue = queue.Queue()

        # Set up an IB Contract for CBA and BHP
        cba = Contract()
        cba.exchange = "SMART"
        cba.symbol = "CBA"
        cba.secType = "STK"
        cba.currency = "AUD"

        bhp = Contract()
        bhp.exchange = "SMART"
        bhp.symbol = "BHP"
        bhp.secType = "STK"
        bhp.currency = "AUD"

        # Create the price handler.
        self.price_handler = IBBarPriceHandler(
            self.ib_service, events_queue, [cba, bhp], self.config
        )

    def test_stream_all_historic_events(self):
        """
        Will test that:
            * historic data is collected from IBService
            * historic data is merge sorted correctly
            * historic data is streamed out correctly
        """
        for i in range(0, 10):
            # Test CBA
            self.price_handler.stream_next()
            self.assertEqual(
                self.price_handler.tickers["CBA"]["timestamp"],
                pd.Timestamp((timestamp + (i * 60)) * 1e9)
            )
            self.assertEqual(
                PriceParser.display(self.price_handler.tickers["CBA"]["close"]),
                closes[i + 1]  # Close is next open
            )

            # Test BHP
            self.price_handler.stream_next()
            self.assertEqual(
                self.price_handler.tickers["BHP"]["timestamp"],
                pd.Timestamp((timestamp + (i * 60)) * 1e9)
            )
            self.assertEqual(
                PriceParser.display(self.price_handler.tickers["BHP"]["close"]),
                closes[i + 1] / 2  # Close is next open
            )

    def test_made_historical_requests(self):
        self.assertEqual(self.ib_service.countHistoricalRequestsMade, 2)


if __name__ == "__main__":
    unittest.main()
