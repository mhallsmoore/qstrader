import unittest

from qstrader.price_handler.ib_bar import IBBarPriceHandler
from qstrader.compat import queue
from qstrader.service.ib import IBService
from qstrader import settings

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
        """
        self.ib_service = IBService()
        self.ib_service.connect("127.0.0.1",4001,0) # TODO remove & replace with mock when happy
        self.ib_service.start()


        self.config = settings.TEST
        fixtures_path = self.config.CSV_DATA_DIR
        events_queue = queue.Queue()
        init_tickers = ["CBA"]
        self.price_handler = IBBarPriceHandler(
            self.ib_service, events_queue, init_tickers, self.config
        )


    def tearDown(self):
        self.ib_service.stop_event.set()
        self.ib_service.join()


    def test(self):
        self.assertEqual(1,2)



if __name__ == "__main__":
    unittest.main()
