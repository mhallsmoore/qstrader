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

from qstrader.broker.zero_broker_commission import ZeroBrokerCommission


class AssetMock(object):
    def __init__(self):
        pass


class BrokerMock(object):
    def __init__(self):
        pass


class ZeroBrokerCommissionTests(unittest.TestCase):
    """Tests the ZeroBrokerCommission class."""

    def test_commission_is_zero_uniformly(self):
        """
        Tests that each method returns zero commission,
        iresspective of asset, consideration or broker.
        """
        zbc = ZeroBrokerCommission()
        asset = AssetMock()
        consideration = 1000.0
        broker = BrokerMock()

        self.assertEqual(
            zbc._calc_commission(asset, consideration, broker=broker),
            0.0
        )
        self.assertEqual(
            zbc._calc_tax(asset, consideration, broker=broker),
            0.0
        )
        self.assertEqual(
            zbc.calc_total_cost(asset, consideration, broker=broker),
            0.0
        )


if __name__ == "__main__":
    unittest.main()
