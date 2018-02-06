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


class ExchangeException(Exception):
    pass


class Exchange(object):
    """This abstract class provides an interface to a
    trading exchange such as the NYSE or LSE. This class
    family is only required for simulations, rather than
    live or paper trading.

    It exposes methods for obtaining Asset pricing
    information, along with a calendar capability for trading
    opening times and market events.

    Unless other data sources are added, in QSTrader the
    Exchange is the canonical source of pricing
    information on an Asset for a simulation.

    A SimulatedBroker entity obtains market prices from a
    derived Exchange class, and in turn the trading
    algorithm entity obtains the market data from the
    SimulatedBroker.
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def is_open_at_datetime(self, dt):
        raise NotImplementedError(
            "Should implement is_open_at_datetime()"
        )

    @abstractmethod
    def is_open_now(self):
        raise NotImplementedError(
            "Should implement is_open_now()"
        )

    @abstractmethod
    def get_latest_asset_bid_ask(self, asset):
        raise NotImplementedError(
            "Should implement get_latest_asset_bid_ask()"
        )
