import unittest

from qstrader.price_parser import PriceParser
from qstrader.price_handler.ib_bar import IBBarPriceHandler
from qstrader.compat import queue
from qstrader import settings


class TestPriceHandlerSimpleCase(unittest.TestCase):
    def setUp(self):
        events_queue = queue.Queue()
        tickers = ["GOOG", "AMZN", "MSFT"]
        self.price_handler = IBBarPriceHandler(
            events_queue, tickers, settings.TEST
        )

    def test_stream_tick(self):
        self.price_handler.stream_next()
        self.assertEqual(1,1)


if __name__ == "__main__":
    unittest.main()
