from qstrader.alpha_model.alpha_model import AlphaModel


class SingleSignalAlphaModel(AlphaModel):
    """
    A simple AlphaModel that provides a single scalar forecast
    value for each Asset in the Universe.

    Parameters
    ----------
    universe : `Universe`
        The Assets to make signal forecasts for.
    signal : `float`, optional
        The single fixed floating point scalar value for the signals.
    data_handler : `DataHandler`, optional
        An optional DataHandler used to preserve interface across AlphaModels.
    """

    def __init__(
        self,
        universe,
        signal=1.0,
        data_handler=None
    ):
        self.universe = universe
        self.signal = signal
        self.data_handler = data_handler

    def __call__(self, dt):
        """
        Produce the dictionary of single fixed scalar signals for
        each of the Asset instances within the Universe.

        Parameters
        ----------
        dt : `pd.Timestamp`
            The time 'now' used to obtain appropriate data and universe
            for the the signals.

        Returns
        -------
        `dict{str: float}`
            The Asset symbol keyed scalar-valued signals.
        """
        assets = self.universe.get_assets(dt)
        return {asset: self.signal for asset in assets}
