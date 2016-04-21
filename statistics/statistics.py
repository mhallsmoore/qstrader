import os, os.path
import pandas as pd
import matplotlib
from abc import ABCMeta, abstractmethod
try:
    matplotlib.use('TkAgg')
except:
    pass
import matplotlib.pyplot as plt
import seaborn as sns
from qstrader import settings

class Statistics(object):
    """
    Statistics is an abstract class providing an interface for 
    all inherited statistic classes (live, historic, custom, etc).

    The goal of a Statistics object is to keep a record of useful
    information about one or many trading strategies as the strategy
    is running. This is done by hooking into the main event loop and
    essentially updating the object according to portfolio performance
    over time.

    Ideally, Statistics should be subclassed according to the strategies
    and timeframes-traded by the user. Different trading strategies
    may require different metrics or frequencies-of-metrics to be updated,
    however the example given is suitable for longer timeframes.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self):
        """
        Update all the statistics according to values of the portfolio
        and open positions. This should be called from within the
        event loop.
        """
        raise NotImplementedError("Should implement update()")

    @abstractmethod
    def get_statistics(self):
        """
        Return a dict containing all statistics.
        """
        raise NotImplementedError("Should implement get_statistics()")

    @abstractmethod
    def plot_results(self):
        """
        Plot all statistics collected up until 'now'
        """
        raise NotImplementedError("Should implement plot_results()")


class SimpleStatistics(Statistics):
    """
    Simple Statistics provides a bare-bones example of statistics
    that can be collected through trading.

    Statistics included are Sharpe Ratio, Drawdown, Max Drawdown,
    Max Drawdown Duration, Total Profit Value and Total Return Pct.

    TODO think about Alpha/Beta, compare strategy of benchmark.
    TODO testing
    TODO think about speed -- will be bad doing for every tick 
    on anything that trades sub-minute.
    TODO think about slippage, fill rate, etc
    TODO remove equity_file references throughout QSTrader
    """
    def __init__(self, portfolio_handler):
        """
        Takes in a portfolio handler.
        """
        self.portfolio_handler = portfolio_handler
        self.sharpe={}
        self.drawdowns=pd.Series()
        self.max_drawdown=0
        self.equity=pd.Series()
        self.equity_returns=pd.Series()
        self.hwm=[float(self.portfolio_handler.portfolio.equity)]

    def update(self, timestamp):
        """
        Update all statistics that must be tracked over time.
        """
        # Retrieve equity value of Portfolio
        self.equity.ix[timestamp]=float(self.portfolio_handler.portfolio.equity)

        # Calculate percentage return between current and previous equity value.
        current_index = len(self.equity)-1
        self.equity_returns.ix[timestamp] = (self.equity.ix[current_index] - self.equity.ix[current_index-1]) / self.equity.ix[current_index-1]

        # Calculate Drawdown. 
        # Note that we have pre-seeded HWM to be starting equity value -- don't add one-too-many values.
        if(current_index>0):
            self.hwm.append(max(self.hwm[current_index-1], self.equity.ix[timestamp]))

        self.drawdowns.ix[timestamp]=self.hwm[current_index]-self.equity.ix[timestamp]

    def get_statistics(self):
        """
        Return a dict with all statistics
        """
        statistics={}
        statistics["sharpe"]=self.sharpe
        statistics["drawdowns"]=self.drawdowns
        statistics["max_drawdown"]=self.max_drawdown
        statistics["equity"]=self.equity
        statistics["equity_returns"]=self.equity_returns
        return statistics

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
        df["equity"]=self.equity
        df["equity_returns"]=self.equity_returns
        df["drawdowns"]=self.drawdowns
        
        # Plot the equity curve
        ax1 = fig.add_subplot(311, ylabel='Equity Value')
        df["equity"].plot(ax=ax1, color=sns.color_palette()[0])

        # Plot the returns
        # df["Returns"]=df["Equity"].pct_change()
        ax2 = fig.add_subplot(312, ylabel='Equity Returns')
        df['equity_returns'].plot(ax=ax2, color=sns.color_palette()[1])

        # drawdown, max_dd, dd_duration = self.create_drawdowns(df["Equity"])
        ax3 = fig.add_subplot(313, ylabel='Drawdowns')
        df['drawdowns'].plot(ax=ax3, color=sns.color_palette()[2])

        # Plot the figure
        plt.show()