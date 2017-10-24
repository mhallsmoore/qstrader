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

from abc import ABCMeta, abstractmethod


class BrokerCommissionException(Exception):
    pass


class BrokerCommission(object):
    """Abstract class to handle the calculation of brokerage
    commission/fees. Includes governmental jurisdiction tax
    (such as equity transaction stamp duty in the UK).
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def _calc_commission(self, asset, consideration, broker=None):
        raise NotImplementedError(
            "Should implement _calc_commission()"
        )

    @abstractmethod
    def _calc_tax(self, asset, consideration, broker=None):
        raise NotImplementedError(
            "Should implement _calc_tax()"
        )

    @abstractmethod
    def calc_total_cost(self, asset, consideration, broker=None):
        raise NotImplementedError(
            "Should implement calc_total_cost()"
        )
