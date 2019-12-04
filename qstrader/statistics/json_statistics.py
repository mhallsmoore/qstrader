import datetime
import json

import numpy as np

import qstrader.statistics.performance as perf


class JSONStatistics(object):
    """
    Standalone class to output basic backtesting statistics
    into a JSON file format.

    Parameters
    ----------
    equity_curve : `pd.DataFrame`
        The equity curve DataFrame indexed by date-time.
    periods : `int`, optional
        The number of periods to use for Sharpe ratio calculation.
    output_filename : `str`
        The filename to output the JSON statistics dictionary to.
    """

    def __init__(
        self,
        equity_curve,
        periods=252,
        output_filename='statistics.json'
    ):
        self.equity_curve = equity_curve
        self.periods = periods
        self.output_filename = output_filename
        self.statistics = self._calculate_statistics()

    @staticmethod
    def _series_to_tuple_list(series):
        """
        Converts Pandas Series indexed by date-time into
        list of tuples indexed by milliseconds since epoch.

        Parameters
        ----------
        series : `pd.Series`
            The Pandas Series to be converted.

        Returns
        -------
        `list[tuple]`
            The list of epoch-indexed tuple values.
        """
        return [
            (
                int(
                    datetime.datetime.combine(
                        k, datetime.datetime.min.time()
                    ).timestamp() * 1000.0
                ), v
            )
            for k, v in series.to_dict().items()
        ]

    def _calculate_statistics(self):
        """
        Creates a dictionary of various statistics associated with
        the backtest of a trading strategy.

        All Pandas Series indexed by date-time are converted into
        milliseconds since epoch representation.

        Returns
        -------
        `dict`
            The statistics dictionary.
        """
        self.equity_curve['Returns'] = self.equity_curve['Equity'].pct_change().fillna(0.0)
        self.equity_curve['CumReturns'] = np.exp(np.log(1 + self.equity_curve['Returns']).cumsum())

        # Drawdown, max drawdown, max drawdown duration
        dd_s, max_dd, dd_dur = perf.create_drawdowns(self.equity_curve['CumReturns'])

        stats = {}

        # Equity curve and returns
        stats['equity_curve'] = JSONStatistics._series_to_tuple_list(
            self.equity_curve['Equity']
        )
        stats['returns'] = JSONStatistics._series_to_tuple_list(
            self.equity_curve['Returns']
        )
        stats['cum_returns'] = JSONStatistics._series_to_tuple_list(
            self.equity_curve['CumReturns']
        )

        # Drawdown statistics
        stats['drawdowns'] = JSONStatistics._series_to_tuple_list(dd_s)
        stats['max_drawdown'] = max_dd
        stats['max_drawdown_duration'] = dd_dur

        # Performance
        stats['cagr'] = perf.create_cagr(
            self.equity_curve['CumReturns'], self.periods
        )
        stats['annualised_vol'] = (
            self.equity_curve['Returns'].std() * np.sqrt(252)
        )
        stats['sharpe'] = perf.create_sharpe_ratio(
            self.equity_curve['Returns'], self.periods
        )
        stats['sortino'] = perf.create_sortino_ratio(
            self.equity_curve['Returns'], self.periods
        )

        return stats

    def to_file(self):
        """
        Outputs the statistics dictionary to a JSON file.
        """
        with open(self.output_filename, 'w') as outfile:
            json.dump(self.statistics, outfile)
