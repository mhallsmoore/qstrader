import unittest
from qstrader import settings
from qstrader.ib import IBCallback, IBClient
"""
TODO - currently actually requires a connection to IBGateway running. Should mock.
"""


class TestIBSetupCase(unittest.TestCase):
    """
    Test that the IB connection can be set up.
    """
    def setUp(self):
        self.ib_cb = IBCallback()
        self.ib_client = IBClient(self.ib_cb, settings.TEST)

    def test_can_connect(self):
        self.assertEqual(self.ib_client.gateway.isConnected(), True)

if __name__ == "__main__":
    unittest.main()
