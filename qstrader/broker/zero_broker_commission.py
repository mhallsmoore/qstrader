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

from qstrader.broker.broker_commission import BrokerCommission


class ZeroBrokerCommission(BrokerCommission):
    """A default BrokerCommission subclass that produces
    no commission or tax. This is the default commission
    model for QSTrader.
    """
    
    def __init__(self):
        pass

    def _calc_commission(self, asset, consideration, broker=None):
        """
        Returns zero commission.
        """
        return 0.0

    def _calc_tax(self, asset, consideration, broker=None):
        """
        Returns zero tax.
        """
        return 0.0

    def calc_total_cost(self, asset, consideration, broker=None):
        """
        Calculate the total of any commission and/or tax
        for the trade of size 'consideration'.
        """
        commission = self._calc_commission(
            asset, consideration, broker
        )
        tax = self._calc_tax(
            asset, consideration, broker
        )
        return commission + tax
