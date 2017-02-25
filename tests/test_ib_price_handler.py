import unittest

from qstrader.price_handler.ib_bar import IBBarPriceHandler
from qstrader.compat import queue
from qstrader import settings

class TestPriceHandlerSimpleCase(unittest.TestCase):
    def setUp(self):
        """
        Set up the PriceHandler object with a small
        set of initial tickers for a backtest in historic mode.
        """
        self.config = settings.TEST
        fixtures_path = self.config.CSV_DATA_DIR
        events_queue = queue.Queue()
        init_tickers = ["CBA"]
        self.price_handler = IBBarPriceHandler(
            events_queue, init_tickers, self.config
        )

    def test(self):
        self.assertEqual(1,2)



if __name__ == "__main__":
    unittest.main()
