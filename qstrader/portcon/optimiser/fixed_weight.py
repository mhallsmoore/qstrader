from qstrader.portcon.optimiser.optimiser import PortfolioOptimiser


class FixedWeightPortfolioOptimiser(PortfolioOptimiser):
    """
    Produces a dictionary keyed by Asset with that utilises the weights
    provided directly. This simply 'passes through' the provided weights
    without modification.

    Parameters
    ----------
    data_handler : `DataHandler`, optional
        An optional DataHandler used to preserve interface across
        TargetWeightGenerators.
    """

    def __init__(
        self,
        data_handler=None
    ):
        self.data_handler = data_handler

    def __call__(self, dt, initial_weights):
        """
        Produce the dictionary of target weight
        values for each of the Asset instances provided.

        Parameters
        ----------
        dt : `pd.Timestamp`
            The time 'now' used to obtain appropriate data for the
            target weights.
        initial_weights : `dict{str: float}`
            The initial weights prior to optimisation.

        Returns
        -------
        `dict{str: float}`
            The Asset symbol keyed scalar-valued target weights.
        """
        return initial_weights
