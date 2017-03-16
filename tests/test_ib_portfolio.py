import unittest
from qstrader.ib_portfolio import IBPortfolio
from qstrader.service.ib import IBService
from qstrader.compat import queue
import time

class TestIBPortfolio(unittest.TestCase):
    def setUp(self):
        """
        Set up IBService.
        Set up IBPortfolio.
        """
        self.ib_service = IBService()
        self.ib_service.connect("127.0.0.1", 4001, 0)
        self.ib_service.start()
        self.portfolio = IBPortfolio(
            self.ib_service, None, 0
        )

    def test_stream_portfolio_updates(self):
        """
        Test that portfolio updates are requested
        Test that portfolio updates show in real time.

        Print portfolio value every second for 1 minute
        """
        for i in range(0, 20):    # Run for about 4 minutes
            time.sleep(10)
            print("time: %s, value: %s" % (i, self.portfolio.equity))

        self.assertEqual(1, 2)


    def tearDown(self):
        self.ib_service.stop_event.set()
        self.ib_service.join()

if __name__ == "__main__":
    unittest.main()
