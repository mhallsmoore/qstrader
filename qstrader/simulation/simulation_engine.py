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


class SimulationEngineException(object):
    pass


class SimulationEngine(object):
    """This abstract class provides an interface to a trading
    event simulation engine.

    Subclasses are designed to take a starting and ending
    timestamps and use them to generate events at a specific
    frequency that corresponds to each 'run' of the trading logic.

    It achieves this by overriding __iter__ and yielding Event
    entities. These entities would include signalling an exchange
    opening, an exchange closing, as well as pre- and post-opening
    events to allow handling of cash-flows and corporate actions.

    In this way the necessary events can be carried out for
    the entities in the system, such as dividend handling,
    capital changes, performance calculations and trading
    orders.
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError(
            "Should implement __iter__()"
        )
