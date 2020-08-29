import numpy as np

from qstrader.portcon.order_sizer.order_sizer import OrderSizer


class LongShortLeveragedOrderSizer(OrderSizer):
    """
    Creates a target portfolio of quantities for each Asset
    using its provided weight and total equity available in the
    Broker portfolio, leveraging up if necessary via the supplied
    gross leverage.

    Parameters
    ----------
    broker : `Broker`
        The derived Broker instance to obtain portfolio equity from.
    broker_portfolio_id : `str`
        The specific portfolio at the Broker to obtain equity from.
    data_handler : `DataHandler`
        To obtain latest asset prices from.
    gross_leverage : `float`, optional
        The amount of percentage leverage to use when sizing orders.
    """

    def __init__(
        self,
        broker,
        broker_portfolio_id,
        data_handler,
        gross_leverage=1.0
    ):
        self.broker = broker
        self.broker_portfolio_id = broker_portfolio_id
        self.data_handler = data_handler
        self.gross_leverage = self._check_set_gross_leverage(
            gross_leverage
        )

    def _check_set_gross_leverage(self, gross_leverage):
        """
        Checks and sets the gross leverage percentage value.

        Parameters
        ----------
        gross_leverage : `float`
            The amount of percentage leverage to use when sizing orders.
            This assumes no restriction on margin.

        Returns
        -------
        `float`
            The gross leverage percentage value.
        """
        if (
            gross_leverage <= 0.0
        ):
            raise ValueError(
                'Gross leverage "%s" provided to long-short levered '
                'order sizer is non positive.' % gross_leverage
            )
        else:
            return gross_leverage

    def _obtain_broker_portfolio_total_equity(self):
        """
        Obtain the Broker portfolio total equity.

        Returns
        -------
        `float`
            The Broker portfolio total equity.
        """
        return self.broker.get_portfolio_total_equity(self.broker_portfolio_id)

    def _normalise_weights(self, weights):
        """
        Rescale provided weight values to ensure the
        weights are scaled to gross exposure divided by
        gross leverage.

        Parameters
        ----------
        weights : `dict{Asset: float}`
            The un-normalised weight vector.

        Returns
        -------
        `dict{Asset: float}`
            The scaled weight vector.
        """
        gross_exposure = sum(np.abs(weight) for weight in weights.values())

        # If the weights are very close or equal to zero then rescaling
        # is not possible, so simply return weights unscaled
        if np.isclose(gross_exposure, 0.0):
            return weights

        gross_ratio = self.gross_leverage / gross_exposure

        return {
            asset: (weight * gross_ratio)
            for asset, weight in weights.items()
        }

    def __call__(self, dt, weights):
        """
        Creates a long short leveraged target portfolio from the
        provided target weights at a particular timestamp.

        Parameters
        ----------
        dt : `pd.Timestamp`
            The current date-time timestamp.
        weights : `dict{Asset: float}`
            The (potentially unnormalised) target weights.

        Returns
        -------
        `dict{Asset: dict}`
            The long short target portfolio dictionary with quantities.
        """
        total_equity = self._obtain_broker_portfolio_total_equity()

        # Pre-cost dollar weight
        N = len(weights)
        if N == 0:
            # No forecasts so portfolio remains in cash
            # or is fully liquidated
            return {}

        # Scale weights to take into account gross exposure and leverage
        normalised_weights = self._normalise_weights(weights)

        target_portfolio = {}
        for asset, weight in sorted(normalised_weights.items()):
            pre_cost_dollar_weight = total_equity * weight

            # Estimate broker fees for this asset
            est_quantity = 0  # TODO: Needs to be added for IB
            est_costs = self.broker.fee_model.calc_total_cost(
                asset, est_quantity, pre_cost_dollar_weight, broker=self.broker
            )

            # Calculate integral target asset quantity assuming broker costs
            after_cost_dollar_weight = pre_cost_dollar_weight - est_costs
            asset_price = self.data_handler.get_asset_latest_ask_price(
                dt, asset
            )

            if np.isnan(asset_price):
                raise ValueError(
                    'Asset price for "%s" at timestamp "%s" is Not-a-Number (NaN). '
                    'This can occur if the chosen backtest start date is earlier '
                    'than the first available price for a particular asset. Try '
                    'modifying the backtest start date and re-running.' % (asset, dt)
                )

            # Truncate the after cost dollar weight
            # to nearest integer
            truncated_after_cost_dollar_weight = (
                np.floor(after_cost_dollar_weight)
                if after_cost_dollar_weight >= 0.0
                else np.ceil(after_cost_dollar_weight)
            )
            asset_quantity = int(
                truncated_after_cost_dollar_weight / asset_price
            )

            # Add to the target portfolio
            target_portfolio[asset] = {"quantity": asset_quantity}

        return target_portfolio
