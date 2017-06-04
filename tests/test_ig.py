import unittest

from qstrader.event import OrderEvent
from qstrader.providers.ig import IGClient

try:
    import Queue as queue
except ImportError:
    import queue

from qstrader import settings

from qstrader.execution_handler.ig import IGExecutionHandler


class TestIGExecutionHandler(unittest.TestCase):
    """
    Test that the IG connection can be set up.
    """
    def setUp(self):
        self.test_sell_event = OrderEvent("CS.D.AUDUSD.TODAY.IP", "SELL", 1)
        self.test_buy_event = OrderEvent("CS.D.AUDUSD.TODAY.IP", "BOT", 1)
        self.events_queue = queue.Queue()
        self.config = settings.from_file(settings.DEFAULT_CONFIG_FILENAME, testing=True)
        self.igclient = IGClient(self.config)

    def test_can_connect(self):
        igexecutionhandler = IGExecutionHandler(self.events_queue, self.igclient.ig_service, self.config)
        self.assertIsInstance(igexecutionhandler, IGExecutionHandler)
        self.assertIsNotNone(igexecutionhandler.execute_order(self.test_sell_event))
        self.assertIsNotNone(igexecutionhandler.execute_order(self.test_buy_event))

    if __name__ == "__main__":
        unittest.main()
