import numpy as np

from qstrader.portcon.order_sizer.order_sizer import OrderSizeGeneration


class DollarWeightedCashBufferedOrderSizeGeneration(OrderSizeGeneration):
    """
    Creates a target portfolio of quantities for each Asset
    using its provided weight and total equity available in the
    Broker portfolio.

    Includes an optional cash buffer due to the non-fractional amount
    of share/unit sizes. The cash buffer defaults to 5% of the total
    equity, but can be modified.

    Parameters
    ----------
    broker : `Broker`
        The derived Broker instance to obtain portfolio equity from.
    broker_portfolio_id : `str`
        The specific portfolio at the Broker to obtain equity from.
    data_handler : `DataHandler`
        To obtain latest asset prices from.
    cash_buffer_percentage : `float`, optional
        The percentage of the portfolio equity to retain in
        cash to avoid generating Orders that exceed account
        equity (assuming no margin available).
    """

    def __init__(
        self,
        broker,
        broker_portfolio_id,
        data_handler,
        cash_buffer_percentage=0.05
    ):
        self.broker = broker
        self.broker_portfolio_id = broker_portfolio_id
        self.data_handler = data_handler
        self.cash_buffer_percentage = self._check_set_cash_buffer(
            cash_buffer_percentage
        )

    def _check_set_cash_buffer(self, cash_buffer_percentage):
        """
        Checks and sets the cash buffer percentage value.

        Parameters
        ----------
        cash_buffer_percentage : `float`
            The percentage of the portfolio equity to retain in
            cash to avoid generating Orders that exceed account
            equity (assuming no margin available).

        Returns
        -------
        `float`
            The cash buffer percentage value.
        """
        if (
            cash_buffer_percentage < 0.0 or cash_buffer_percentage > 1.0
        ):
            raise ValueError(
                'Cash buffer percentage "%s" provided to dollar-weighted '
                'execution algorithm is negative or '
                'exceeds 100%.' % cash_buffer_percentage
            )
        else:
            return cash_buffer_percentage

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
        Rescale provided weight values to ensure
        weight vector sums to unity.

        Parameters
        ----------
        weights : `dict{Asset: float}`
            The un-normalised weight vector.

        Returns
        -------
        `dict{Asset: float}`
            The unit sum weight vector.
        """
        if any([weight < 0.0 for weight in weights.values()]):
            raise ValueError(
                'Dollar-weighted cash-buffered order sizing does not support '
                'negative weights. All positions must be long-only.'
            )

        weight_sum = sum(weight for weight in weights.values())

        # If the weights are very close or equal to zero then rescaling
        # is not possible, so simply return weights unscaled
        if np.isclose(weight_sum, 0.0):
            return weights

        return {
            asset: (weight / weight_sum)
            for asset, weight in weights.items()
        }

    def __call__(self, dt, weights):
        """
        Creates a dollar-weighted cash-buffered target portfolio from the
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
            The cash-buffered target portfolio dictionary with quantities.
        """
        total_equity = self._obtain_broker_portfolio_total_equity()
        cash_buffered_total_equity = total_equity * (
            1.0 - self.cash_buffer_percentage
        )

        # Pre-cost dollar weight
        N = len(weights)
        if N == 0:
            # No forecasts so portfolio remains in cash
            # or is fully liquidated
            return {}

        # Ensure weight vector sums to unity
        normalised_weights = self._normalise_weights(weights)

        target_portfolio = {}
        for asset, weight in sorted(normalised_weights.items()):
            pre_cost_dollar_weight = cash_buffered_total_equity * weight

            # Estimate broker fees for this asset
            est_quantity = 0  # TODO: Needs to be added for IB
            est_costs = self.broker.fee_model.calc_total_cost(
                asset, est_quantity, pre_cost_dollar_weight, broker=self.broker
            )

            # Calculate integral target asset quantity assuming broker costs
            after_cost_dollar_weight = pre_cost_dollar_weight - est_costs
            asset_price = self.data_handler.get_asset_latest_ask_price(
                dt, asset
            )  # Long only
            asset_quantity = int(
                np.floor(after_cost_dollar_weight / asset_price)
            )

            # Add to the target portfolio
            target_portfolio[asset] = {"quantity": asset_quantity}

        return target_portfolio
