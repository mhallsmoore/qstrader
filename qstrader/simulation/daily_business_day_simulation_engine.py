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

import datetime

import pandas as pd
from pandas.tseries.offsets import BDay
import pytz

from qstrader.simulation.simulation_engine import (
    SimulationEngine, SimulationEngineException
)
from qstrader.simulation.simulation_event import (
    SimulationEvent
)


class DailyBusinessDaySimulationEngine(SimulationEngine):
    """A SimulationEngine subclass that generates events on a daily
    frequency defaulting to Western-style business days, that is
    Monday-Friday.

    In particular it does not take into account any specific
    regional holidays, such as Federal Holidays in the USA or
    Bank Holidays in the UK.

    It produces a pre-market event, a market open event,
    a market closing event and a post-market event for every day
    between the starting and ending dates.
    """

    def __init__(self, starting_day, ending_day):
        """
        Initialise the start and end days.
        """
        self.starting_day = starting_day
        self.ending_day = ending_day
        if ending_day < starting_day:
            raise SimulationEngineException(
                "Ending date time %s is less than starting date time %s. "
                "Cannot create DailyBusinessDaySimulationEngine "
                "instance." % (
                    self.ending_day, self.starting_day
                )
            )
        self.business_days = self._generate_business_days()

    def _generate_business_days(self):
        """
        Generate the list of business days using midnight UTC as
        the timestamp.
        """
        days = pd.date_range(
            self.starting_day, self.ending_day, freq=BDay()
        )
        return days

    def __iter__(self):
        """
        Generate the daily timestamps and event information
        for pre-market, market open, market close and post-market.
        """
        for index, bday in enumerate(self.business_days):
            year = bday.year
            month = bday.month
            day = bday.day

            yield SimulationEvent(
                pd.Timestamp(
                    datetime.datetime(year, month, day), tz='UTC'
                ), event_type="pre_market"
            )
            yield SimulationEvent(
                pd.Timestamp(
                    datetime.datetime(year, month, day, 9, 30),
                    tz=pytz.timezone('US/Eastern')
                ).tz_convert(pytz.utc), event_type="market_open"
            )
            yield SimulationEvent(
                pd.Timestamp(
                    datetime.datetime(year, month, day, 16, 0),
                    tz=pytz.timezone('US/Eastern')
                ).tz_convert(pytz.utc), event_type="market_close"
            )
            yield SimulationEvent(
                pd.Timestamp(
                    datetime.datetime(year, month, day, 23, 59), tz='UTC'
                ), event_type="post_market"
            )
