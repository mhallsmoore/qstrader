# The MIT License (MIT)
#
# Copyright (c) 2015 QuantStart.com, QuarkGluon Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math

from qstrader.algo.pcm import PortfolioConstructionModel


class FixedWeightPCM(PortfolioConstructionModel):
    """
    A derived PortfolioConstructionModel class that produces fixed
    proportion (but potentially unequal) 'dollar' weighting for all
    Asset entities provided in the list of Forecasts, using the
    Forecast 'value' as the weight proportion.

    This value -should- add to one, but if it does not it will be
    rescaled such that the new proportion per asset will be
    fractionally reduced.

    All forecast values must be positive or an exception is raised.

    Example:
    [Forecast(AAPL, 0.4), Forecast(GOOG, 0.3), Forecast(AMZN, 0.5)]
    -> Total value of forecast does not sum to 1.0, instead it is: 1.2
    -> Therefore:
        AAPL becomes 0.4/1.2, GOOG becomes 0.3/1.2, AMZN becomes 0.5/1.2

    It achieves this through the following procedure:
    * Query the Broker entity for the current total market value
        of the Portfolio
    * Estimate the dollar weight of each asset
    * Estimate the likely transaction costs and subtract to leave
        consideration cash available per Asset
    * Divide the consideration by the current market price of the
        Asset and create a desired portfolio with the appropriate
        (conservative) number of shares.

    Parameters
    ----------
    start_dt : pd.Timestamp
        The starting date of the PortfolioConstructionModel
    broker : Broker
        A handle to the live or simulated Broker entity
    broker_portfolio_id : int
        The ID of the portfolio as stored by the Broker entity
    risk_model : RiskModel, optional
        A handle to the RiskModel that governs overall portfolio
        risk behaviour
    transaction_cost_model : TransactionCostModel, optional
        A handle to the TransactionCostModel which governs estimates
        of transaction costs for purposes of estimating trade profits
    """

    def __init__(
        self, start_dt, broker,
        broker_portfolio_id, risk_model=None,
        transaction_cost_model=None
    ):
        super().__init__(
            start_dt, broker,
            broker_portfolio_id,
            risk_model=risk_model,
            transaction_cost_model=transaction_cost_model
        )

    def _check_all_forecasts(self, forecasts):
        """
        Checks that all forecasts are both sane and long-only.
        """
        sane = self._check_sane_forecasts(forecasts)
        long_only = self._check_long_only_forecasts(forecasts)
        return (sane and long_only)

    def _construct_scaled_forecast_weights(self):
        """
        Sum the total forecast values and rescale them to ensure
        total forecast values sum to 1.0.
        """
        total_forecast = sum(forecast.value for forecast in self.forecasts)
        asset_weights = dict(
            (forecast.asset, forecast.value / total_forecast)
            for forecast in self.forecasts
        )
        return asset_weights

    def _construct_desired_alpha_portfolio(self):
        """
        Creates a fixed proportion dollar weighted portfolio of the
        provided Forecasts that rescales the forecast 'values' if they
        do not sum to 1.0.
        """
        # Obtain the current portfolio market value
        port_market_value = self.broker.get_portfolio_total_market_value(
            self.broker_portfolio_id
        )

        # Pre-cost dollar weight
        N = len(self.forecasts)
        if N == 0:
            # No forecasts so portfolio remains in cash
            # or is fully liquidated
            return {}

        # Fixed proportion dollar weighting portfolio construction
        alpha_portfolio = {}
        scaled_forecast_weights = self._construct_scaled_forecast_weights()
        for forecast in self.forecasts:
            asset = forecast.asset
            asset_weight = scaled_forecast_weights[asset]
            pc_dollar_weight = port_market_value * asset_weight
            # Calculate tax and commission for this asset
            # (note some assets are tax free)
            est_commission = self.transaction_cost_model._calc_commission(
                asset, pc_dollar_weight, self.broker
            )
            est_tax = self.transaction_cost_model._calc_tax(
                asset, pc_dollar_weight
            )

            # Use this to create an actual quantity of shares
            ac_dollar_weight = (pc_dollar_weight - est_commission - est_tax)
            asset_market_value = self.broker.get_latest_asset_price(asset)[1]  # Ask
            alpha_portfolio[asset] = {
                "quantity": int(
                    math.floor(ac_dollar_weight / asset_market_value)
                )
            }

        return alpha_portfolio
