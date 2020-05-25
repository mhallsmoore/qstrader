class SignalsCollection(object):
    """
    Provides a mechanism for aggregating all signals
    used by AlphaModels or RiskModels.

    Keeps track of updating the asset universe for each signal
    if a DynamicUniverse is utilised.

    Ensures each signal receives a new data point at the
    appropriate simulation iteration rate.

    Parameters
    ----------
    signals : `dict{str: Signal}`
        Map of signal name to derived instance of Signal
    data_handler : `DataHandler`
        The data handler used to obtain pricing.
    """

    def __init__(self, signals, data_handler):
        self.signals = signals
        self.data_handler = data_handler
        self.warmup = 0  # Used for 'burn in'

    def __getitem__(self, signal):
        """
        Allow Signal to be returned via dictionary-like syntax.

        Parameters
        ----------
        signal : `str`
            The signal string.

        Returns
        -------
        `Signal`
            The signal instance.
        """
        return self.signals[signal]

    def update(self, dt):
        """
        Updates the universe (if dynamic) for each signal as well
        as the pricing information for this timestamp.

        Parameters
        ----------
        dt : `pd.Timestamp`
            The time at which the signals are to be updated for.
        """
        # Ensure any new assets in a DynamicUniverse
        # are added to the signal
        for name, signal in self.signals.items():
            self.signals[name].update_assets(dt)

        # Update all of the signals with new prices
        for name, signal in self.signals.items():
            assets = signal.assets
            for asset in assets:
                price = self.data_handler.get_asset_latest_mid_price(dt, asset)
                self.signals[name].append(asset, price)
        self.warmup += 1
