import numpy as np

from qstrader.signals.buffer import AssetPriceBuffers


class TrendSignal(object):
    """
    Indicator class to calculate lookback-period trend
    (based on a simple moving average of last N periods)
    for a set of prices.

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

    def _simple_moving_average(self, asset, lookback):
        """
        Calculate the 'trend' for the provided lookback
        period based on the simple moving average of the
        price buffers for a particular asset.

        Parameters
        ----------
        asset : `str`
            The asset symbol name.
        lookback : `int`
            The lookback period.

        Returns
        -------
        `float`
            The SMA value ('trend') for the period.
        """
        prices = self.buffers.prices['%s_%s' % (asset, lookback)]
        if len(prices) < lookback:
            raise ValueError(
                'Number of price values (%s) is less than lookback '
                'period (%s). Not calculating trend/SMA.' % (
                    len(prices), lookback
                )
            )
        return np.mean(prices)

    def __call__(self, asset, lookback):
        """
        Calculate the lookback-period trend
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
            The trend (SMA) for the period.
        """
        return self._simple_moving_average(asset, lookback)
