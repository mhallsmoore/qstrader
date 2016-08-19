import unittest

from qstrader.price_handler.ib_bar import IBBarPriceHandler
from qstrader.compat import queue
from qstrader import settings


class TestPriceHandlerSimpleCase(unittest.TestCase):
    def setUp(self):
        self.events_queue = queue.Queue()
        tickers = ["FB", "AMZN"]
        self.price_handler = IBBarPriceHandler(
            self.events_queue, tickers, settings.TEST
        )

    def test_historic_bar(self):
        event = self.events_queue.get()
        self.assertNotEqual(event, None)

if __name__ == "__main__":
    unittest.main()
