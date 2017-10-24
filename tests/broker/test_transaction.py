# The MIT License (MIT)
#
# Copyright (c) 2015 QuantStart.com, QuarkGluon Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest

import pandas as pd

from qstrader.broker.transaction import Transaction


class EquityMock(object):
    """Mock object for the Asset-derived Equity class."""

    def __init__(self, asset_id, exchange=None):
        self.__name__ = "Equity"
        self.asset_id = asset_id
        self.exchange = exchange

    def __str__(self):
        return "%s(%s)" % (self.__name__, self.asset_id)


class TransactionTests(unittest.TestCase):
    """Tests that the Transaction class correctly assigns
    its attributes and that the object representation
    correctly recreates the object.
    """

    def test_transaction_representation(self):
        """
        Tests that the Transaction representation
        correctly recreates the object.
        """
        dt = pd.Timestamp('2015-05-06')
        asset = EquityMock(1, exchange='NYSE')
        transaction = Transaction(
            asset, quantity=168, dt=dt, price=56.18, order_id=153
        )
        exp_repr = (
            "Transaction(asset=Equity(1), quantity=168, "
            "dt=2015-05-06 00:00:00, price=56.18, order_id=153)"
        )
        self.assertEqual(repr(transaction), exp_repr)


if __name__ == "__main__":
    unittest.main()
