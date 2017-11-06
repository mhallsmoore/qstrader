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

from qstrader.algo.pcm import (
    PortfolioConstructionModel,
    PortfolioConstructionModelException
)


class EqualWeightPCM(PortfolioConstructionModel):
    """
    A derived PortfolioConstructionModel class that produces equal
    'dollar' weighting for all Asset entities provided in the list
    of Forecasts.

    It achieves this through the following procedure:
    * Query the Broker entity for the current total market value
        of the Portfolio
    * Estimate the dollar weight of each asset on a 1/N basis
        for all N assets
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

    def _construct_desired_alpha_portfolio(self):
        """
        Creates an equal dollar weighted portfolio of the
        provided Forecasts irrespective of the Forecast weights
        on a 1/N basis, for N assets.
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
        asset_weight = 1.0/float(N)
        pc_dollar_weight = port_market_value * asset_weight

        # Equal dollar weighting portfolio construction
        alpha_portfolio = {}
        for forecast in self.forecasts:
            asset = forecast.asset
            # Calculate tax and commission for this asset
            # (note some assets are tax free)
            est_commission = self.transaction_cost_model._calc_commission(
                asset, pc_dollar_weight, self.broker
            )
            est_tax = self.transaction_cost_model._calc_tax(
                asset, pc_dollar_weight, self.broker
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
