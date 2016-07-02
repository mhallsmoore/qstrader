from .base import AbstractStatistics

import pandas as pd
import numpy as np
import matplotlib
from decimal import Decimal
try:
    matplotlib.use('TkAgg')
except:
    pass
import matplotlib.pyplot as plt
import seaborn as sns


class SimpleStatistics(AbstractStatistics):
    """
    Simple Statistics provides a bare-bones example of statistics
    that can be collected through trading.

    Statistics included are Sharpe Ratio, Drawdown, Max Drawdown,
    Max Drawdown Duration.

    TODO think about Alpha/Beta, compare strategy of benchmark.
    TODO think about speed -- will be bad doing for every tick
    on anything that trades sub-minute.
    TODO think about slippage, fill rate, etc
    TODO brokerage costs?

    TODO need some kind of trading-frequency parameter in setup.
    Sharpe calculations need to know if daily, hourly, minutely, etc.
    """
    def __init__(self, portfolio_handler):
        """
        Takes in a portfolio handler.
        """
        self.portfolio_handler = portfolio_handler
        self.drawdowns = pd.Series()
        self.equity = pd.Series()
        self.equity_returns = pd.Series()
        # Initialize in order for first-step calculations to be correct.
        self.hwm = [float(self.portfolio_handler.portfolio.equity)]
        self.equity.ix["0000-00-00 00:00:00"] = float(self.portfolio_handler.portfolio.equity)

    def update(self, timestamp):
        """
        Update all statistics that must be tracked over time.
        """
        # Retrieve equity value of Portfolio
        self.equity.ix[timestamp] = float(self.portfolio_handler.portfolio.equity)
        current_index = len(self.equity) - 1

        # Calculate percentage return between current and previous equity value.
        self.equity_returns.ix[timestamp] = (
            (Decimal(self.equity.ix[current_index]) - Decimal(self.equity.ix[current_index - 1])) /
            Decimal(self.equity.ix[current_index])
        ) * 100
        self.equity_returns.ix[timestamp] = \
            Decimal(self.equity_returns.ix[timestamp]).quantize(Decimal("0.0001"))

        # Calculate Drawdown.
        # Note that we have pre-seeded HWM to be starting equity value,
        # so we don't seed it twice, else we'd add one-too-many values.
        if(current_index > 0):
            self.hwm.append(
                max(self.hwm[current_index - 1], self.equity.ix[timestamp])
            )

        self.drawdowns.ix[timestamp] = (
            self.hwm[current_index] - self.equity.ix[timestamp]
        )

    def get_results(self):
        """
        Return a dict with all important results & stats.
        """
        statistics = {}
        statistics["sharpe"] = self.calculate_sharpe()
        statistics["drawdowns"] = self.drawdowns
        statistics["max_drawdown"] = max(self.drawdowns)
        statistics["max_drawdown_pct"] = self.calculate_max_drawdown_pct()
        statistics["equity"] = self.equity
        statistics["equity_returns"] = self.equity_returns
        return statistics

    def calculate_sharpe(self, benchmark_return=0.00):
        """
        Calculate the sharpe ratio of our equity_returns.

        Expects benchmark_return to be, for example, 0.01 for 1%

        TOOD TEST
        """
        excess_returns = self.equity_returns.astype(float) - benchmark_return / 252

        # Return the annualised Sharpe ratio based on the excess daily returns
        return round(self.annualised_sharpe(excess_returns), 4)

    def annualised_sharpe(self, returns, N=252):
        """
        Calculate the annualised Sharpe ratio of a returns stream
        based on a number of trading periods, N. N defaults to 252,
        which then assumes a stream of daily returns.

        The function assumes that the returns are the excess of
        those compared to a benchmark.
        """
        return Decimal(np.sqrt(N) * returns.mean() / returns.std()).quantize(Decimal("0.0001"))

    def calculate_max_drawdown_pct(self):
        """
        Calculate the percentage drop related to the "worst"
        drawdown seen.
        """
        bottom_index = self.drawdowns.idxmax()
        top_index = self.equity[:bottom_index].idxmax()
        pct = (
            (self.equity.ix[top_index] - self.equity.ix[bottom_index]) /
            self.equity.ix[top_index] * 100
        )
        return Decimal(pct).quantize(Decimal("0.0001"))

    def plot_results(self):
        """
        A simple script to plot the balance of the portfolio, or
        "equity curve", as a function of time.
        """
        sns.set_palette("deep", desat=.6)
        sns.set_context(rc={"figure.figsize": (8, 4)})

        # Plot two charts: Equity curve, period returns
        fig = plt.figure()
        fig.patch.set_facecolor('white')

        df = pd.DataFrame()
        df["equity"] = self.equity
        df["equity_returns"] = self.equity_returns
        df["drawdowns"] = self.drawdowns

        # Plot the equity curve
        ax1 = fig.add_subplot(311, ylabel='Equity Value')
        df["equity"].plot(ax=ax1, color=sns.color_palette()[0])

        # Plot the returns
        ax2 = fig.add_subplot(312, ylabel='Equity Returns')
        df['equity_returns'].astype(float).plot(ax=ax2, color=sns.color_palette()[1])

        # drawdown, max_dd, dd_duration = self.create_drawdowns(df["Equity"])
        ax3 = fig.add_subplot(313, ylabel='Drawdowns')
        df['drawdowns'].plot(ax=ax3, color=sns.color_palette()[2])

        # Plot the figure
        plt.show()
