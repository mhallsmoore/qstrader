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

import numpy as np

from qstrader.exchange.exchange import (
    Exchange, ExchangeException
)
from qstrader.exchange.price_volume_data_source import (
    PriceVolumeDataSourceException
)


class SimulatedExchange(Exchange):
    """The SimulatedExchange class is used to model a live
    trading venue. Its task is to initialise a set of provided
    PriceVolumeDataSource instances (RDBMS, CSV, time series DB).

    The model exposes a get_latest_asset_price method, which queries
    each data source in turn in an attempt to find the latest known
    price for the asset, based on provided historical or simulated
    asset data.

    It also exposes methods to inform a client class intance of
    when the exchange is open (and thus can receive Orders).
    """

    def __init__(self, start_dt, data_sources):
        """
        Initialise the SimulatedExchange.
        """
        self.start_dt = start_dt
        self.cur_dt = start_dt
        self.data_sources = data_sources

    def is_open_at_datetime(self, dt):
        """
        Check if the SimulatedExchange is open at a particular
        provided pandas Timestamp.
        """
        # TODO: Utilise an exchange calendar to adjust this.
        return True

    def is_open_now(self):
        """
        Check if the SimulatedExchange is open "now", as far as
        the Exchange understands "now" (via its cur_dt attribute).
        """
        # TODO: Utilise an exchange calendar to adjust this.
        return True

    def get_latest_asset_bid_ask(self, asset):
        """
        Iteratively checks each provided data source for the
        availability of an Asset price and returns (bid, ask),
        if available.

        For OHLCV data this returns (midpoint, midpoint). If no
        price is available this returns (np.NaN, np.NaN).
        """
        for ds in self.data_sources:
            if ds.asset == asset:
                try:
                    ds_price = ds.get_latest_asset_price_at_dt(self.cur_dt)
                except PriceVolumeDataSourceException:
                    pass
                else:
                    return ds_price
        return (np.NaN, np.NaN)

    def update(self, dt):
        """
        Update the current time for the SimulatedExchange.
        """
        if dt < self.cur_dt:
            raise ExchangeException(
                'Provided datetime (%s) is earlier than '
                'current exchange datetime (%s). Cannot '
                'update Exchange.' % (dt, self.cur_dt)
            )
        else:
            self.cur_dt = dt
