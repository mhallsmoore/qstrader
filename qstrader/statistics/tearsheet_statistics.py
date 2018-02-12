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

from matplotlib.ticker import FuncFormatter
from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import seaborn as sns

import qstrader.statistics.performance as perf
from qstrader.statistics.statistics import Statistics


class TearsheetStatistics(Statistics):
    """
    Displays a Matplotlib-generated 'one-pager' as often
    found in institutional strategy performance reports.
    """
    def __init__(
        self, broker, title=None, periods=252
    ):
        self.broker = broker
        self.title = title
        self.periods = periods
        self.equity = []

    def update(self, dt):
        """
        Update all statistics that must be tracked over time.
        """
        self.equity.append(
            (dt, self.broker.get_account_total_equity()["master"])
        )

    def get_results(self):
        """
        Return a dict with all important results & stats.
        """
        # Equity
        equity_df = pd.DataFrame(self.equity, columns=["timestamp", "equity"])
        equity_df.set_index("timestamp", inplace=True)

        # Returns
        equity_df["returns"] = equity_df["equity"].pct_change().fillna(0.0)

        # Cummulative Returns
        equity_df["cum_returns"] = np.exp(np.log(1 + equity_df["returns"]).cumsum())

        # Drawdown, max drawdown, max drawdown duration
        dd_s, max_dd, dd_dur = perf.create_drawdowns(equity_df["cum_returns"])

        # Equity statistics
        statistics = {}
        statistics["sharpe"] = perf.create_sharpe_ratio(
            equity_df["returns"], self.periods
        )
        statistics["drawdowns"] = dd_s
        statistics["max_drawdown"] = max_dd
        statistics["max_drawdown_pct"] = max_dd
        statistics["max_drawdown_duration"] = dd_dur
        statistics["equity"] = equity_df["equity"]
        statistics["returns"] = equity_df["returns"]
        statistics["cum_returns"] = equity_df["cum_returns"]
        return statistics

    def _plot_equity(self, stats, ax=None, **kwargs):
        """
        Plots cumulative rolling returns versus some benchmark.
        """
        def format_two_dec(x, pos):
            return '%.2f' % x

        equity = stats['cum_returns']

        if ax is None:
            ax = plt.gca()

        y_axis_formatter = FuncFormatter(format_two_dec)
        ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))
        ax.xaxis.set_tick_params(reset=True)
        ax.yaxis.grid(linestyle=':')
        ax.xaxis.set_major_locator(mdates.YearLocator(1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.grid(linestyle=':')

        equity.plot(lw=2, color='green', alpha=0.6, x_compat=False,
                    label='Backtest', ax=ax, **kwargs)

        ax.axhline(1.0, linestyle='--', color='black', lw=1)
        ax.set_ylabel('Cumulative returns')
        ax.legend(loc='best')
        ax.set_xlabel('')
        plt.setp(ax.get_xticklabels(), visible=True, rotation=0, ha='center')
        return ax

    def _plot_drawdown(self, stats, ax=None, **kwargs):
        """
        Plots the underwater curve
        """
        def format_perc(x, pos):
            return '%.0f%%' % x

        drawdown = stats['drawdowns']

        if ax is None:
            ax = plt.gca()

        y_axis_formatter = FuncFormatter(format_perc)
        ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))
        ax.yaxis.grid(linestyle=':')
        ax.xaxis.set_tick_params(reset=True)
        ax.xaxis.set_major_locator(mdates.YearLocator(1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.grid(linestyle=':')

        underwater = -100 * drawdown
        underwater.plot(ax=ax, lw=2, kind='area', color='red', alpha=0.3, **kwargs)
        ax.set_ylabel('')
        ax.set_xlabel('')
        plt.setp(ax.get_xticklabels(), visible=True, rotation=0, ha='center')
        ax.set_title('Drawdown (%)', fontweight='bold')
        return ax

    def _plot_monthly_returns(self, stats, ax=None, **kwargs):
        """
        Plots a heatmap of the monthly returns.
        """
        returns = stats['returns']
        if ax is None:
            ax = plt.gca()

        monthly_ret = perf.aggregate_returns(returns, 'monthly')
        monthly_ret = monthly_ret.unstack()
        monthly_ret = np.round(monthly_ret, 3)
        monthly_ret.rename(
            columns={1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
                     5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
                     9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'},
            inplace=True
        )

        sns.heatmap(
            monthly_ret.fillna(0) * 100.0,
            annot=True,
            fmt="0.1f",
            annot_kws={"size": 8},
            alpha=1.0,
            center=0.0,
            cbar=False,
            cmap=cm.RdYlGn,
            ax=ax, **kwargs)
        ax.set_title('Monthly Returns (%)', fontweight='bold')
        ax.set_ylabel('')
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        ax.set_xlabel('')

        return ax

    def _plot_yearly_returns(self, stats, ax=None, **kwargs):
        """
        Plots a barplot of returns by year.
        """
        def format_perc(x, pos):
            return '%.0f%%' % x

        returns = stats['returns']

        if ax is None:
            ax = plt.gca()

        y_axis_formatter = FuncFormatter(format_perc)
        ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))
        ax.yaxis.grid(linestyle=':')

        yly_ret = perf.aggregate_returns(returns, 'yearly') * 100.0
        yly_ret.plot(ax=ax, kind="bar")
        ax.set_title('Yearly Returns (%)', fontweight='bold')
        ax.set_ylabel('')
        ax.set_xlabel('')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        ax.xaxis.grid(False)

        return ax

    def _plot_txt_curve(self, stats, ax=None, **kwargs):
        """
        Outputs the statistics for the equity curve.
        """
        def format_perc(x, pos):
            return '%.0f%%' % x

        returns = stats["returns"]
        cum_returns = stats['cum_returns']

        trd_yr = 0

        if ax is None:
            ax = plt.gca()

        y_axis_formatter = FuncFormatter(format_perc)
        ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

        tot_ret = cum_returns[-1] - 1.0
        cagr = perf.create_cagr(cum_returns, self.periods)
        sharpe = perf.create_sharpe_ratio(returns, self.periods)
        sortino = perf.create_sortino_ratio(returns, self.periods)
        dd, dd_max, dd_dur = perf.create_drawdowns(cum_returns)

        ax.text(0.25, 8.9, 'Total Return', fontsize=8)
        ax.text(7.50, 8.9, '{:.0%}'.format(tot_ret), fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 7.9, 'CAGR', fontsize=8)
        ax.text(7.50, 7.9, '{:.2%}'.format(cagr), fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 6.9, 'Sharpe Ratio', fontsize=8)
        ax.text(7.50, 6.9, '{:.2f}'.format(sharpe), fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 5.9, 'Sortino Ratio', fontsize=8)
        ax.text(7.50, 5.9, '{:.2f}'.format(sortino), fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 4.9, 'Annual Volatility', fontsize=8)
        ax.text(7.50, 4.9, '{:.2%}'.format(returns.std() * np.sqrt(252)), fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 3.9, 'R-Squared', fontsize=8)
        ax.text(7.50, 3.9, 'N/A', fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 2.9, 'Max Daily Drawdown', fontsize=8)
        ax.text(7.50, 2.9, '{:.2%}'.format(dd_max), color='red', fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 1.9, 'Max Drawdown Duration', fontsize=8)
        ax.text(7.50, 1.9, '{:.0f}'.format(dd_dur), fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 0.9, 'Trades per Year', fontsize=8)
        ax.text(7.50, 0.9, '{:.1f}'.format(trd_yr), fontweight='bold', horizontalalignment='right', fontsize=8)
        ax.set_title('Curve', fontweight='bold')

        ax.grid(False)
        ax.spines['top'].set_linewidth(2.0)
        ax.spines['bottom'].set_linewidth(2.0)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_visible(False)
        ax.set_ylabel('')
        ax.set_xlabel('')

        ax.axis([0, 10, 0, 10])
        return ax

    def plot_results(self, filename=None):
        """
        Plot the Tearsheet
        """
        rc = {
            'lines.linewidth': 1.0,
            'axes.facecolor': '0.995',
            'figure.facecolor': '0.97',
            'font.family': 'serif',
            'font.serif': 'Ubuntu',
            'font.monospace': 'Ubuntu Mono',
            'font.size': 10,
            'axes.labelsize': 10,
            'axes.labelweight': 'bold',
            'axes.titlesize': 10,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8,
            'legend.fontsize': 10,
            'figure.titlesize': 12
        }
        sns.set_context(rc)
        sns.set_style("whitegrid")
        sns.set_palette("deep", desat=.6)

        vertical_sections = 5
        fig = plt.figure(figsize=(10, 12))
        fig.suptitle(self.title, y=0.94, weight='bold')
        gs = gridspec.GridSpec(vertical_sections, 3, wspace=0.25, hspace=0.5)

        stats = self.get_results()
        ax_equity = plt.subplot(gs[:2, :])
        ax_drawdown = plt.subplot(gs[2, :])
        ax_monthly_returns = plt.subplot(gs[3, :2])
        ax_yearly_returns = plt.subplot(gs[3, 2])
        ax_txt_curve = plt.subplot(gs[4, 0])
        # ax_txt_trade = plt.subplot(gs[4, 1])
        # ax_txt_time = plt.subplot(gs[4, 2])

        self._plot_equity(stats, ax=ax_equity)
        self._plot_drawdown(stats, ax=ax_drawdown)
        self._plot_monthly_returns(stats, ax=ax_monthly_returns)
        self._plot_yearly_returns(stats, ax=ax_yearly_returns)
        self._plot_txt_curve(stats, ax=ax_txt_curve)
        # self._plot_txt_trade(stats, ax=ax_txt_trade)
        # self._plot_txt_time(stats, ax=ax_txt_time)

        # Plot the figure
        plt.show()
