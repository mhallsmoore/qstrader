import unittest
import mock
import queue
import numpy as np
import pandas as pd
from qstrader.price_parser import PriceParser
from qstrader.price_handler.ib_bar import IBBarPriceHandler
from qstrader.compat import queue
from qstrader.service.ib import IBService
from qstrader import settings
from ibapi.contract import *


# Starting at 2017-01-01 13:00:00, 1 minute bars.
timestamp = 1483275600
closes = np.arange(80.00, 91.00, 1)


class IBServiceMock(object):
    def __init__(self):
        self.historicalDataQueue = queue.Queue()
        self.waitingHistoricalData = []
        self.countHistoricalRequestsMade = 0
        # Populate some historic data for the mock service.
        # CBA mock data
        for i in range(0,10):
            self.historicalDataQueue.put((0, timestamp + (i * 60),
                                            closes[i], closes[i]+1,
                                            closes[i]-1, closes[i+1],
                                            1000000, 100, closes[i], False))
        # BHP mock data
        for i in range(0,10):
            self.historicalDataQueue.put((1, timestamp + (i * 60),
                                            closes[i]/2, closes[i]+1/2,
                                            (closes[i]-1)/2, closes[i+1]/2,
                                            1000000, 100, closes[i]/2, False))

    def reqHistoricalData(self, *arg):
        self.countHistoricalRequestsMade += 1



class TestPriceHandlerSimpleCase(unittest.TestCase):
    def setUp(self):
        """
        Set up the PriceHandler object with a small
        set of initial tickers for a backtest in historic mode.

        For now, while testing locally with IB (i.e. not Travis), implement
        all real IB functionality (i.e. set up service)

        TODO:
            * Mock IB Service, populate dummy data.
            * Duplicate tests from test_price_handler
            * Add test to all price_handlers for get_last_close()
            * Test multiple tickers
            * Test multiple timeframes
            * Test returned date formats
            * Test mocked live market data methods
        """
        self.ib_service = IBServiceMock()
        self.config = settings.TEST
        fixtures_path = self.config.CSV_DATA_DIR
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
            self.ib_service, events_queue, [cba,bhp], self.config
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
                pd.Timestamp((timestamp + (i*60)) * 1e9)
            )
            self.assertEqual(
                PriceParser.display(self.price_handler.tickers["CBA"]["close"]),
                closes[i+1] # Close is next open
            )

            # Test BHP
            self.price_handler.stream_next()
            self.assertEqual(
                self.price_handler.tickers["BHP"]["timestamp"],
                pd.Timestamp((timestamp + (i*60)) * 1e9)
            )
            self.assertEqual(
                PriceParser.display(self.price_handler.tickers["BHP"]["close"]),
                closes[i+1]/2 # Close is next open
            )

    def test_made_historical_requests(self):
        self.assertEqual(self.ib_service.countHistoricalRequestsMade, 2)

    def test_can_handle_all_bar_sizes(self):
        self.assertEqual(1, 2)





if __name__ == "__main__":
    unittest.main()
