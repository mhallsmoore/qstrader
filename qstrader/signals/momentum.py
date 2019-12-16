import numpy as np
import pandas as pd

from qstrader.signals.buffer import AssetPriceBuffers


class MomentumSignal(object):
    """
    """

    def __init__(self, assets, lookbacks=[12]):
        self.assets = assets
        self.lookbacks = lookbacks
        self.buffers = self._create_asset_price_buffers()

    def _create_asset_price_buffers(self):
        """
        """
        return AssetPriceBuffers(
            self.assets, lookbacks=self.lookbacks
        )

    def append(self, asset, price):
        """
        """
        self.buffers.append(asset, price)

    def _cumulative_return(self, asset, lookback):
        """
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
        """
        return self._cumulative_return(asset, lookback)