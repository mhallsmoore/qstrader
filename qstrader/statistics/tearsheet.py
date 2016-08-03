from .base import AbstractStatistics
from ..compat import pickle
from ..price_parser import PriceParser

from datetime import datetime
from matplotlib.ticker import FuncFormatter
from matplotlib import cm

import qstrader.statistics.performance as perf

import os
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
import seaborn as sns


class TearsheetStatistics(AbstractStatistics):
    """
    """
    def __init__(self, config, portfolio_handler, title=None, benchmark=None):
        """
        Takes in a portfolio handler.
        """
        self.config = config
        self.portfolio_handler = portfolio_handler
        self.title = '\n'.join(title)
        self.benchmark = benchmark
        self.equity = {}
        self.equity_benchmark = {}
        self.log_scale = False


    def update(self, timestamp, portfolio_handler):
        """
        Update all statistics that must be tracked over time.
        """
        self.equity[timestamp] = PriceParser.display(
            portfolio_handler.portfolio.equity
        )


    def get_results(self):
        """
        Return a dict with all important results & stats.
        """
        # Equity
        equity_s = pd.Series(self.equity).sort_index()

        # Returns
        returns_s = equity_s.pct_change().fillna(0.0)

        # Cummulative Returns
        cum_returns_s = np.exp(np.log(1 + returns_s).cumsum())

        # Drawdown, max drawdown, max drawdown duration
        dd_s, max_dd, dd_dur = perf.create_drawdowns(cum_returns_s)

        statistics = {}
        statistics["sharpe"] = perf.create_sharpe_ratio(returns_s)
        statistics["drawdowns"] = dd_s
        statistics["max_drawdown"] = max_dd  #TODO: is DD amt really needed?
        statistics["max_drawdown_pct"] = max_dd
        statistics["max_drawdown_duration"] = dd_dur
        statistics["equity"] = equity_s
        statistics["returns"] = returns_s
        statistics["cum_returns"] = cum_returns_s

        return statistics


    def _get_positions(self):
        """
        Retrieve the list of closed Positions objects from the portfolio
        and reformat into a pandas dataframe to be returned
        """
        pos = self.portfolio_handler.portfolio.closed_positions
        a = []
        for p in pos:
            a.append(p.__dict__)

        df = pd.DataFrame(a)
        x = lambda x: PriceParser.display(x)

        df['avg_bot'] = df['avg_bot'].apply(x)
        df['avg_price'] = df['avg_price'].apply(x)
        df['avg_sld'] = df['avg_sld'].apply(x)
        df['cost_basis'] = df['cost_basis'].apply(x)
        df['init_commission'] = df['init_commission'].apply(x)
        df['init_price'] = df['init_price'].apply(x)
        df['market_value'] = df['market_value'].apply(x)
        df['net'] = df['net'].apply(x)
        df['net_incl_comm'] = df['net_incl_comm'].apply(x)
        df['net_total'] = df['net_total'].apply(x)
        df['realised_pnl'] = df['realised_pnl'].apply(x)
        df['total_bot'] = df['total_bot'].apply(x)
        df['total_commission'] = df['total_commission'].apply(x)
        df['total_sld'] = df['total_sld'].apply(x)
        df['unrealised_pnl'] = df['unrealised_pnl'].apply(x)

        return df


    def _plot_equity(self, equity, benchmark=None, ax=None, **kwargs):
        """
        Plots cumulative rolling returns versus some benchmark.
        """
        def format_two_dec(x, pos): return '%.2f' % x

        if ax is None:
            ax = plt.gca()

        y_axis_formatter = FuncFormatter(format_two_dec)
        ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))
        ax.xaxis.set_tick_params(reset=True)
        ax.xaxis.set_major_locator(mdates.YearLocator(1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

        """
        if benchmark is not None:
            benchmark.plot(
                lw=2, color='gray', label='S&P500', alpha=0.60, ax=ax, **kwargs
            )
        """

        equity.plot(lw=2, color='green', alpha=0.6, x_compat=False,
                    label='Backtest', ax=ax, **kwargs)

        ax.axhline(1.0, linestyle='--', color='black', lw=1)
        ax.set_ylabel('Cumulative returns')
        ax.legend(loc='best')
        ax.set_xlabel('')

        if self.log_scale:
            ax.set_yscale('log')

        return ax


    def _plot_drawdown(self, drawdown, ax=None, **kwargs):
        """
        Plots the underwater curve
        """
        def format_perc(x, pos): return '%.0f%%' % x

        if ax is None:
            ax = plt.gca()

        y_axis_formatter = FuncFormatter(format_perc)
        ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

        underwater = -100 * drawdown
        underwater.plot(ax=ax, lw=2, kind='area', color='red', alpha=0.3, **kwargs)
        ax.set_ylabel('')
        ax.set_xlabel('')
        ax.set_title('Drawdown (%)', fontweight='bold')
        return ax


    def _plot_monthly_returns(self, returns, ax=None, **kwargs):
        """
        Plots a heatmap of the monthly returns.
        """
        if ax is None:
            ax = plt.gca()

        monthly_ret = perf.aggregate_returns(returns, 'monthly')
        monthly_ret = monthly_ret.unstack()
        monthly_ret = np.round(monthly_ret, 3)
        monthly_ret.rename(columns={1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
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


    def _plot_yearly_returns(self, returns, ax=None, **kwargs):
        """
        Plots a barplot of returns by year.
        """
        def format_perc(x, pos): return '%.0f%%' % x

        if ax is None:
            ax = plt.gca()

        y_axis_formatter = FuncFormatter(format_perc)
        ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

        yly_ret = perf.aggregate_returns(returns, 'yearly') * 100.0
        yly_ret.plot(ax=ax, kind="bar")
        ax.set_title('Yearly Returns (%)', fontweight='bold')
        ax.set_ylabel('')
        ax.set_xlabel('')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

        return ax


    def _plot_txt_curve(self, returns, cum_returns, positions, benchmark_returns,
                       ax=None, **kwargs):
        """
        Outputs the statistics for the equity curve.
        """
        def format_perc(x, pos): return '%.0f%%' % x

        if ax is None:
            ax = plt.gca()

        y_axis_formatter = FuncFormatter(format_perc)
        ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

#        equity_b = cum_returns(returns_b, starting_value=1.0)
        tot_ret = cum_returns[-1] - 1.0
#        tot_ret_b = equity_b[-1] - 1.0
        cagr = perf.create_cagr(cum_returns)
#        cagr_b = perf.create_cagr(equity_b)
        sharpe = perf.create_sharpe_ratio(returns)
#        sharpe_b = perf.create_sharpe_ratio(returns_b)
        sortino = perf.create_sortino_ratio(returns)
#        sortino_b = perf.create_sortino_ratio(returns_b)
        rsq = perf.rsquared(range(cum_returns.shape[0]), cum_returns)
#        rsq_b = perf.rsquared(range(equity_b.shape[0]), equity_b)
        dd, dd_max, dd_dur = perf.create_drawdowns(cum_returns)
#        dd_b, dd_max_b, dd_dur_b = perf.create_drawdowns(equity_b)
        trd_yr = positions.shape[0] / ((returns.index[-1] - returns.index[0]).days / 365.0)

        ax.text(0.25, 8.9, 'Total Return', fontsize=8)
        ax.text(7.50, 8.9, '{:.0%}'.format(tot_ret), fontweight='bold', horizontalalignment='right', fontsize=8)
#        ax.text(9.75, 8.9, '{:.0%}'.format(tot_ret_b), fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 7.9, 'CAGR', fontsize=8)
        ax.text(7.50, 7.9, '{:.2%}'.format(cagr), fontweight='bold', horizontalalignment='right', fontsize=8)
#        ax.text(9.75, 7.9, '{:.2%}'.format(cagr_b), fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 6.9, 'Sharpe Ratio', fontsize=8)
        ax.text(7.50, 6.9, '{:.2f}'.format(sharpe), fontweight='bold', horizontalalignment='right', fontsize=8)
#        ax.text(9.75, 6.9, '{:.2f}'.format(sharpe_b), fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 5.9, 'Sortino Ratio', fontsize=8)
        ax.text(7.50, 5.9, '{:.2f}'.format(sortino), fontweight='bold', horizontalalignment='right', fontsize=8)
#        ax.text(9.75, 5.9, '{:.2f}'.format(sortino_b), fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 4.9, 'Annual Volatility', fontsize=8)
        ax.text(7.50, 4.9, '{:.2%}'.format(returns.std() * np.sqrt(252)), fontweight='bold', horizontalalignment='right', fontsize=8)
#        ax.text(9.75, 4.9, '{:.2%}'.format(returns_b.std() * np.sqrt(252)), fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 3.9, 'R-Squared', fontsize=8)
        ax.text(7.50, 3.9, '{:.2f}'.format(rsq), fontweight='bold', horizontalalignment='right', fontsize=8)
#        ax.text(9.75, 3.9, '{:.2f}'.format(rsq_b), fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 2.9, 'Max Daily Drawdown', fontsize=8)
        ax.text(7.50, 2.9, '{:.2%}'.format(dd_max), color='red', fontweight='bold', horizontalalignment='right', fontsize=8)
#        ax.text(9.75, 2.9, '{:.2%}'.format(dd_max_b), color='red', fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 1.9, 'Max Drawdown Duration', fontsize=8)
        ax.text(7.50, 1.9, '{:.0f}'.format(dd_dur), fontweight='bold', horizontalalignment='right', fontsize=8)
#        ax.text(9.75, 1.9, '{:.0f}'.format(dd_dur_b), fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.text(0.25, 0.9, 'Trades per Year', fontsize=8)
        ax.text(7.50, 0.9, '{:.1f}'.format(trd_yr), fontweight='bold', horizontalalignment='right', fontsize=8)

        ax.set_title('Curve vs. Benchmark', fontweight='bold')
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


    def plot_results(self):
        """
        Plot the Tearsheet
        """
        rc = {'lines.linewidth': 1.0,
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
        fig = plt.figure(figsize=(10, vertical_sections * 3))
        fig.suptitle(self.title, y=0.96)
        gs = gridspec.GridSpec(vertical_sections, 3, wspace=0.25, hspace=0.5)

        stats = self.get_results()
        positions = self._get_positions()

        ax_equity = plt.subplot(gs[:2, :])
        ax_drawdown = plt.subplot(gs[2, :], sharex=ax_equity)
        ax_monthly_returns = plt.subplot(gs[3, :2])
        ax_yearly_returns = plt.subplot(gs[3, 2])
        ax_txt_curve = plt.subplot(gs[4, 0])
        ax_txt_trade = plt.subplot(gs[4, 1])
        ax_txt_time = plt.subplot(gs[4, 2])

        self._plot_equity(stats['cum_returns'], ax=ax_equity)
        self._plot_drawdown(stats['drawdowns'], ax=ax_drawdown)
        self._plot_monthly_returns(stats['returns'], ax=ax_monthly_returns)
        self._plot_yearly_returns(stats['returns'], ax=ax_yearly_returns)
        self._plot_txt_curve(stats["returns"], stats['cum_returns'],
                             self._get_positions(), None, ax=ax_txt_curve)
#        self._plot_txt_trade(positions, ax=ax_txt_trade)
#        self._plot_txt_time(equity["Returns"], ax=ax_txt_time)

        # Plot the figure
        plt.show()


    def get_filename(self, filename=""):
        if filename == "":
            now = datetime.utcnow()
            filename = "statistics_" + now.strftime("%Y-%m-%d_%H%M%S") + ".pkl"
            filename = os.path.expanduser(os.path.join(self.config.OUTPUT_DIR, filename))
        return filename

    def save(self, filename=""):
        filename = self.get_filename(filename)
        #print("Save results to '%s'" % filename)
        #with open(filename, 'wb') as fd:
        #    pickle.dump(self, fd)
