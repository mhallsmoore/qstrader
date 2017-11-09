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


class AlphaModelException(Exception):
    pass


class AlphaModel(object):
    """Abstract base class to inherit from when generating
    a new alpha/factor/forecast model.

    A derived-class instance of AlphaModel takes in a list
    of Asset instances, a list of external (non-pricing/fundamental)
    data sources and produces a list of Forecast instances.

    These Forecasts are used by the PortfolioConstructionModel
    to generate Orders.

    The AlphaModel framework is generic enough to support many
    types of forecast model, such as short- and long-term trend-
    following, mean-reversion, momentum etc.

    The AlphaModel exposes two 'public' methods - update(dt) and
    forecast().

    update(dt) requires a timestamp and is used to call further
    'private' methods that update the pricing and non-pricing
    data sources.

    forecast() produces the list of actual forecasts and is where
    the alpha/forecast model code is to be called.
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def update(self, dt):
        raise NotImplementedError(
            "Should implement update()"
        )

    @abstractmethod
    def forecast(self):
        raise NotImplementedError(
            "Should implement forecast()"
        )
