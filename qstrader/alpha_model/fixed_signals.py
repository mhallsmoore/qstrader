from qstrader.alpha_model.alpha_model import AlphaModel


class FixedSignalsAlphaModel(AlphaModel):
    """
    A simple AlphaModel that provides a single scalar forecast
    value for each Asset in the Universe.

    Parameters
    ----------
    signal_weights : `dict{str: float}`
        The signal weights per asset symbol.
    universe : `Universe`, optional
        The Assets to make signal forecasts for.
    data_handler : `DataHandler`, optional
        An optional DataHandler used to preserve interface across AlphaModels.
    """

    def __init__(
        self,
        signal_weights,
        universe=None,
        data_handler=None
    ):
        self.signal_weights = signal_weights
        self.universe = universe
        self.data_handler = data_handler

    def __call__(self, dt):
        """
        Produce the dictionary of fixed scalar signals for
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
        return self.signal_weights
