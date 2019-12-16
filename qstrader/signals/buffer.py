from collections import deque
import itertools


class AssetPriceBuffers(object):
    """
    """

    def __init__(self, assets, lookbacks=[12]):
        self.assets = assets
        self.lookbacks = lookbacks
        self.prices = self._create_prices_dict()

    @staticmethod
    def _asset_lookback_key(asset, lookback):
        """
        """
        return '%s_%s' % (asset, lookback)

    def _create_prices_dict(self):
        """
        """
        return {
            AssetPriceBuffers._asset_lookback_key(
                asset, lookback
            ): deque(maxlen=lookback + 1)
            for asset, lookback in itertools.product(
                self.assets, self.lookbacks
            )
        }

    def append(self, asset, price):
        """
        """
        if price <= 0.0:
            raise ValueError(
                'Unable to append non-positive price of "%0.2f" '
                'to metrics buffer for Asset "%s".' % (price, asset) 
            )
        for lookback in self.lookbacks:
            self.prices[
                AssetPriceBuffers._asset_lookback_key(
                    asset, lookback
                )
            ].append(price)