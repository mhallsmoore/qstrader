import numpy as np
import pandas as pd

from qstrader.signals.signal import Signal


class VolatilitySignal(Signal):
    """
    Indicator class to calculate lookback-period daily
    volatility of returns, which is then annualised.

    If the number of available returns is less than the
    lookback parameter the volatility is calculated on
    this subset.

    Parameters
    ----------
    start_dt : `pd.Timestamp`
        The starting datetime (UTC) of the signal.
    universe : `Universe`
        The universe of assets to calculate the signals for.
    lookbacks : `list[int]`
        The number of lookback periods to store prices for.
    """

    def __init__(self, start_dt, universe, lookbacks):
        bumped_lookbacks = [lookback + 1 for lookback in lookbacks]
        super().__init__(start_dt, universe, bumped_lookbacks)

    @staticmethod
    def _asset_lookback_key(asset, lookback):
        """
        Create the buffer dictionary lookup key based
        on asset name and lookback period.

        Parameters
        ----------
        asset : `str`
            The asset symbol name.
        lookback : `int`
            The lookback period.

        Returns
        -------
        `str`
            The lookup key.
        """
        return '%s_%s' % (asset, lookback + 1)

    def _annualised_vol(self, asset, lookback):
        """
        Calculate the annualised volatility for the provided
        lookback period based on the price buffers for a
        particular asset.

        Parameters
        ----------
        asset : `str`
            The asset symbol name.
        lookback : `int`
            The lookback period.

        Returns
        -------
        `float`
            The annualised volatility of returns.
        """
        series = pd.Series(
            self.buffers.prices[
                VolatilitySignal._asset_lookback_key(
                    asset, lookback
                )
            ]
        )
        returns = series.pct_change().dropna().to_numpy()

        if len(returns) < 1:
            return 0.0
        else:
            return np.std(returns) * np.sqrt(252)

    def __call__(self, asset, lookback):
        """
        Calculate the annualised volatility of
        returns for the asset.

        Parameters
        ----------
        asset : `str`
            The asset symbol name.
        lookback : `int`
            The lookback period.

        Returns
        -------
        `float`
            The annualised volatility of returns.
        """
        return self._annualised_vol(asset, lookback)
