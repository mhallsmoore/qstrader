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

from qstrader.statistics.statistics import Statistics

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class SimpleStatistics(Statistics):
    """
    SimpleStatistics provides a bare-bones example of statistics
    that can be collected through trading.
    """

    def __init__(self, broker):
        """
        Takes in a Broker to obtain performance information.
        """
        self.broker = broker
        self.equity = []

    def update(self, dt):
        """
        Update all statistics that must be tracked over time.
        """
        self.equity.append(
            (dt, self.broker.get_account_total_equity()["master"])
        )

    def calc_equity(self):
        """
        Calculate the equity curve
        """
        df = pd.DataFrame(self.equity, columns=["Timestamp", "Equity"])
        return df

    def plot_results(self):
        """
        A simple script to plot the balance of the portfolio, or
        "equity curve", as a function of time.
        """
        df = self.calc_equity()

        sns.set_palette("deep", desat=.6)
        sns.set_context(rc={"figure.figsize": (12, 9)})

        # Plot two charts: Equity curve, period returns
        fig = plt.figure()
        fig.patch.set_facecolor('white')

        # Plot the equity curve
        ax1 = fig.add_subplot(111, ylabel='Gain ($)')
        df["Equity"].plot(ax=ax1, color=sns.color_palette()[0])

        # Rotate dates
        fig.autofmt_xdate()

        # Plot the figure
        plt.show()
