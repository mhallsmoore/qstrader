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

import pandas as pd
import pytz

from qstrader.algo.rebalance import Rebalance, RebalanceException


class WeeklyRebalance(Rebalance):
    """This subclass generates a list of rebalance timestamps
    for pre- or post-market, for a particular trading day of
    the week between the starting and ending dates provided.

    All timestamps produced are set to UTC.
    """

    def __init__(
        self, start_date, end_date,
        weekday, pre_market=True
    ):
        """
        Initialise the WeeklyRebalance instance.
        """
        self.weekday = self._set_weekday(weekday)
        self.start_date = start_date
        self.end_date = end_date
        self.pre_market_time = self._set_market_time(pre_market)
        self.rebalances = self._generate_rebalances()

    def _set_weekday(self, weekday):
        """
        Checks that the weekday string corresponds to
        a business weekday.
        """
        weekdays = ("MON", "TUE", "WED", "THU", "FRI")
        if weekday.upper() not in weekdays:
            raise RebalanceException(
                "Provided weekday keyword '%s' is not recognised "
                "or not a valid weekday." % weekday
            )
        else:
            return weekday.upper()

    def _set_market_time(self, pre_market):
        """
        TODO: Fill in doc string!
        """
        return "00:00:00" if pre_market else "23:59:00"

    def _generate_rebalances(self):
        """
        TODO: Fill in doc string!
        """
        rebalance_dates = pd.date_range(
            start=self.start_date,
            end=self.end_date,
            freq='W-%s' % self.weekday
        )
        rebalance_times = [
            pd.Timestamp(
                "%s %s" % (date, self.pre_market_time),
                tz=pytz.utc
            )
            for date in rebalance_dates
        ]
        return rebalance_times

    def output_rebalances(self):
        """
        TODO: Fill in doc string!
        """
        return self.rebalances
