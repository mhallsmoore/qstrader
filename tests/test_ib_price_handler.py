import unittest

from qstrader.price_parser import PriceParser
from qstrader.price_handler.ib_bar import IBBarPriceHandler
from qstrader.compat import queue
from qstrader import settings


class TestPriceHandlerSimpleCase(unittest.TestCase):
    def setUp(self):
        self.events_queue = queue.Queue()
        tickers = ["RBS", "AMZN"]
        self.price_handler = IBBarPriceHandler(
            self.events_queue, tickers, settings.TEST
        )

    def test_historic_bar(self):
        self.price_handler.stream_next()
        event = self.events_queue.get()
        print(event)
        self.assertNotEqual(event, None)


if __name__ == "__main__":
    unittest.main()
