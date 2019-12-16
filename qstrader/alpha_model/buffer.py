from abc import ABCMeta, abstractmethod

from qstrader.alpha_model.alpha_model import AlphaModel


class BufferAlphaModel(AlphaModel):
    """
    An abstract AlphaModel that makes use of price buffer
    signals in its construction. This is used for, e.g.
    momentum and/or trend-following indicator signals.

    It is necessary to override the 'generate_signals'
    method in a derived subclass in order to implement
    signal logic.

    Parameters
    ----------
    buffer_types : `list[SignalType]`
        The list of buffer type class names needing
        calculation for the alpha model.
    start_dt : `pd.Timestamp`
        The starting datetime (UTC) of the buffering.
    universe : `Universe`
        The univers of assets to create buffers for.
    data_handler : `DataHandler`
        The data handler used to obtain current prices from.
    lookbacks : `list[int]`, optional
        The optional list of lookback periods to calculate
        price buffers for.
    """

    __metaclass__ = ABCMeta

    def __init__(
        self, buffer_types, start_dt, universe,
        data_handler, lookbacks=[12]
    ):
        self.buffer_types = buffer_types
        self.start_dt = start_dt
        self.universe = universe
        self.data_handler = data_handler
        self.lookbacks = lookbacks
        self.buffers = self._generate_asset_signal_buffers()
        self.warmups = 0

    def _generate_asset_signal_buffers(self):
        """
        Generates a dictionary of asset signal buffers
        for each specified signal.

        Returns
        -------
        `dict{str: SignalType}`
            The dictionary of signal type buffers.
        """
        assets = self.universe.get_assets(self.start_dt)
        return {
            buffer_type.__name__.replace('Signal', '').lower(): buffer_type(
                assets, lookbacks=self.lookbacks
            )
            for buffer_type in self.buffer_types
        }

    @abstractmethod
    def generate_signals(self, dt, weights):
        """
        It is necessary to override this method in a
        derived subclass in order to implement signal logic.
        """
        raise NotImplementedError(
            "Must override generate_signals in order to specify "
            "buffer strategy logic."
        )

    def __call__(self, dt):
        """
        Appends all prices to the necessary signal buffers
        for each asset in the universe. Also keeps track of
        warmup/burn-in time so that signals are only generated
        when sufficient data exists.

        Parameters
        ----------
        dt : `pd.Timetamp`
            The current time of the trading system.

        Returns
        -------
        `dict{str: float}`
            The generated signal weights of the alpha model.
        """
        assets = self.universe.get_assets(dt)
        weights = {asset: 0.0 for asset in assets}

        for asset in assets:
            price = self.data_handler.get_asset_latest_mid_price(dt, asset)
            for buffer_type in self.buffer_types:
                buffer_name = buffer_type.__name__.replace('Signal', '').lower()
                self.buffers[buffer_name].append(asset, price)
        self.warmups += 1

        if self.warmups > max(self.lookbacks):
            weights = self.generate_signals(dt, weights)

        return weights
