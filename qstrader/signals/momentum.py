import numpy as np
import pandas as pd

from qstrader.signals.buffer import AssetPriceBuffers


class MomentumSignal(object):
    """
    Indicator class to calculate lookback-period momentum
    (based on cumulative return of last N periods) for
    a set of prices.

    Parameters
    ----------
    assets : `list[str]`
        The list of assets to create price buffers for.
    lookbacks : `list[int]`, optional
        The number of lookback periods to store prices for.
    """

    def __init__(self, assets, lookbacks=[12]):
        self.assets = assets
        self.lookbacks = lookbacks
        self.buffers = self._create_asset_price_buffers()

    def _create_asset_price_buffers(self):
        """
        Create an AssetPriceBuffers instance.

        Returns
        -------
        `AssetPriceBuffers`
            Stores the asset price buffers for the signal.
        """
        return AssetPriceBuffers(
            self.assets, lookbacks=self.lookbacks
        )

    def append(self, asset, price):
        """
        Append a new price onto the price buffer for
        the specific asset provided.

        Parameters
        ----------
        asset : `str`
            The asset symbol name.
        price : `float`
            The new price of the asset.
        """
        self.buffers.append(asset, price)

    def _cumulative_return(self, asset, lookback):
        """
        Calculate the cumulative returns for the provided
        lookback period ('momentum') based on the price
        buffers for a particular asset.

        Parameters
        ----------
        asset : `str`
            The asset symbol name.
        lookback : `int`
            The lookback period.

        Returns
        -------
        `float`
            The cumulative return ('momentum') for the period.
        """
        series = pd.Series(
            self.buffers.prices['%s_%s' % (asset, lookback)]
        )
        returns = series.pct_change().dropna().to_numpy()

        if len(returns) < lookback:
            raise ValueError(
                'Number of returns values (%s) is less than lookback '
                'period (%s). Not calculating cumulative return.' % (
                    len(returns), lookback
                )
            )
        return (np.cumprod(1.0 + np.array(returns)) - 1.0)[-1]

    def __call__(self, asset, lookback):
        """
        Calculate the lookback-period momentum
        for the asset.

        Parameters
        ----------
        asset : `str`
            The asset symbol name.
        lookback : `int`
            The lookback period.

        Returns
        -------
        `float`
            The momentum for the period.
        """
        return self._cumulative_return(asset, lookback)
