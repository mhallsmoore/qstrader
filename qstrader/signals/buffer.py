from collections import deque
import itertools


class AssetPriceBuffers(object):
    """
    Utility class to store double-ended queue ("deque")
    based price buffers for usage in lookback-based
    indicator calculations.

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
        self.prices = self._create_prices_dict()

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
        return '%s_%s' % (asset, lookback)

    def _create_prices_dict(self):
        """
        Creates a dictionary of asset-lookback pair
        price buffers.

        Returns
        -------
        `dict{str: deque[float]}`
            The price buffer dictionary.
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
        Append a new price onto the price deque for
        the specific asset provided.

        Parameters
        ----------
        asset : `str`
            The asset symbol name.
        price : `float`
            The new price of the asset.
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
