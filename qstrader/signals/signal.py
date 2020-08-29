from abc import ABCMeta, abstractmethod

from qstrader.signals.buffer import AssetPriceBuffers


class Signal(object):
    """
    Abstract class to provide historical price range-based
    rolling signals utilising deque-based 'buffers'.

    Parameters
    ----------
    start_dt : `pd.Timestamp`
        The starting datetime (UTC) of the signal.
    universe : `Universe`
        The universe of assets to calculate the signals for.
    lookbacks : `list[int]`
        The number of lookback periods to store prices for.
    """

    __metaclass__ = ABCMeta

    def __init__(self, start_dt, universe, lookbacks):
        self.start_dt = start_dt
        self.universe = universe
        self.lookbacks = lookbacks
        self.assets = self.universe.get_assets(start_dt)
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

    def update_assets(self, dt):
        """
        Ensure that any new additions to the universe also receive
        a price buffer at the point at which they enter.

        Parameters
        ----------
        dt : `pd.Timestamp`
            The update timestamp for the signal.
        """
        universe_assets = self.universe.get_assets(dt)

        # TODO: Assume universe never decreases for now
        extra_assets = list(set(universe_assets) - set((self.assets)))
        for extra_asset in extra_assets:
            self.assets.append(extra_asset)

    @abstractmethod
    def __call__(self, asset, lookback):
        raise NotImplementedError(
            "Should implement __call__()"
        )
