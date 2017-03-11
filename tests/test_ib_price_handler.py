import unittest
from unittest.mock import MagicMock

from qstrader.price_handler.ib_bar import IBBarPriceHandler
from qstrader.compat import queue
from qstrader.service.ib import IBService
from qstrader import settings
from ibapi.contract import *

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
        self.ib_service = MagicMock()
        self.config = settings.TEST
        fixtures_path = self.config.CSV_DATA_DIR
        events_queue = queue.Queue()

        # Set up an IB Contract/
        contract = Contract()
        contract.exchange = "SMART"
        contract.symbol = "CBA"
        contract.secType = "STK"
        contract.currency = "AUD"

        # Create the price handler.
        self.price_handler = IBBarPriceHandler(
            self.ib_service, events_queue, [contract], self.config
        )

    def test_stream_all_historic_events(self):
        """
        Will test that:
            * historic data is collected from IBService
            * historic data is merge sorted correctly
            * historic data is streamed out correctly
        """
        self.assertEqual(1, 2)

    def test_made_historical_requests(self):
        self.assertEqual(1, 2)

    def test_can_handle_all_bar_sizes(self):
        self.assertEqual(1, 2)

    def test_can_do_reqid_to_ticker_lookup(self):
        self.assertEqual(1, 2)

    def test_get_best_bid_ask(self):
        self.assertEqual(1, 2)





if __name__ == "__main__":
    unittest.main()
