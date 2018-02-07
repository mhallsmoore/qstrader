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

from qstrader.exchange.asset import Asset
from qstrader.algo.order import Order


class PortfolioConstructionModelException(Exception):
    pass


class PortfolioConstructionModel(object):
    """This base class is responsible for converting AlphaModel
    forecasts into explicit Order entities that are sent to
    the brokerage.

    It achieves this by having (optional) references to the
    following entities:

    * Broker - Provides updates on the current live/simulated
        portfolio as well as cash balances. [NON-OPTIONAL]
    * RiskModel - Provides veto power over the construction
        methodology based on various risk factors, such as market
        risk, sector risk, leverage, volatility etc. [OPTIONAL]
    * TransactionCostModel - A model that estimates the transaction
        costs of carrying out any Orders and cancels them using logic
        similar to the following: If the expected profit on the trade
        is less than the expected transaction cost. [OPTIONAL]

    On each 'hearbeat' or 'update' the PCM accepts a new list of Asset
    Forecast entities, which are used as guidance for constructing the
    initial desired portfolio. This is then passed through the
    RiskModel checks and any orders are modified. Finally it is passed
    through the TransactionCostModel checks, which may modify or cancel
    orders further.

    At this stage a 'diff' between the current live/simulated Portfolio
    (as far as the Broker understands it) and the desired portfolio is
    created, which then leads to a set of Order objects.

    Example portfolio construction methodologies (that would be
    implemented by inheriting this PortfolioConstructionModel) could include:

    * Equal weighting of assets by position 'dollar' value
    * Inverse volatility weighting (aka 'Risk Parity') using some form
    of historical, or future-looking, measure/estimate of volatility
    (e.g. trailing annual standard deviation of returns).
    * Modern Portfolio Theory/Mean-Variance Optimisation
    * Hierarchical Risk Parity - Marcos Lopez de Prado's HRP algorithm

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
        self, start_dt, broker, broker_portfolio_id,
        risk_model=None, transaction_cost_model=None,
        rebalance_times=None
    ):
        """
        Initialise the PortfolioConstructionModel.
        """
        self.start_dt = start_dt
        self.broker = broker
        self.broker_portfolio_id = broker_portfolio_id
        self.risk_model = risk_model
        self.transaction_cost_model = transaction_cost_model
        self.rebalance_times = rebalance_times
        # Set current time and list of forecasts
        self.forecasts = []
        self.cur_dt = start_dt

    def _check_sane_forecasts(self, forecasts):
        """
        Checks the list of Forecast objects to ensure that
        they are consistent and provide sane values.
        """
        for forecast in forecasts:
            if not issubclass(type(forecast.asset), Asset):
                raise PortfolioConstructionModelException(
                    'Forecast contains a non-Asset asset type: "%s". '
                    'Cannot set the list of forecasts in the Portfolio'
                    'ConstructionModel.' % forecast.asset
                )
            if not type(forecast.value) == float:
                raise PortfolioConstructionModelException(
                    'Forecast contains a non floating point value: "%s" for '
                    'its forecast value. Cannot set the list of forecasts '
                    'in the PortfolioConstructionModel.' % forecast.value
                )
        return True

    def _check_long_only_forecasts(self, forecasts):
        """
        Checks the list of Forecast objects to ensure that
        all values are positive.
        """
        for forecast in forecasts:
            if forecast.value < 0.0:
                raise PortfolioConstructionModelException(
                    'Forecast contains a negative value: "%s" for '
                    'its forecast value. This is interpreted as a short. '
                    'Cannot set the list of forecasts '
                    'in the PortfolioConstructionModel.' % forecast.value
                )
        return True

    def _check_all_forecasts(self, forecasts):
        """
        Method to be overridden by child class that determines
        which forecast restrictions are to be carried out.
        """
        return self._check_sane_forecasts(forecasts)

    def _construct_desired_alpha_portfolio(self):
        """
        Construct the initial desired portfolio solely utilising
        the Forecast list sent from the set of AlphaModel instances.

        This is where any position sizing logic will be included
        in subclasses that does not depend upon risk factors calculated
        by the RiskModel or costs of trading as estimated by the
        TransactionCostModel.

        Example for subclass:
        For an equal 'dollar' weighting of positions, all Asset entities
        would be given a fixed 'dollar' position weighting with
        appropriate orders, irrespective of the Forecast value,
        in this method.
        """
        return {}

    def _construct_desired_risk_portfolio(self, alpha_portfolio):
        """
        Modify the desired portfolio based on the previously
        generated alpha_portfolio, that accounts for the set of
        risks specified within the RiskModel.

        The RiskModel has the power to add, modify or cancel
        Order entities based on risk controls specified within it.

        Example:
        The RiskModel may want to add a market hedge order to
        eliminate exposure to market risk. Since the previous 'alpha'
        portfolio was created solely on Forecasts of Assets, the
        logic to hedge out a market index (say) will be added to
        the RiskModel and will be used to add a hedged Order entity
        to the new DesiredPortfolio instance.
        """
        return alpha_portfolio

    def _construct_desired_trans_cost_portfolio(
        self, risk_portfolio
    ):
        """
        Modify the desired portfolio based on the previously
        generated risk_portfolio, that accounts for the set of
        transaction costs to carry out the trade as estimated
        by the TransactionCostModel.

        The TransactionCostModel has the power to modify or
        cancel Order entities based on the expected cost of
        the Order and the likely profit of the trade.
        """
        return risk_portfolio

    def _diff_desired_broker_portfolios(
        self, desired_portfolio, broker_portfolio
    ):
        """
        Takes a desired portfolio instance as generated by one
        of the previous _construct_desired_****_portfolio methods
        and compares it against a Broker portfolio (live or simulated).

        The difference ('diff') of the two is then used to generate
        a list of Order entities.
        """
        # Make sure all keys end up in both dictionaries
        # with quantity equal to zero if not in a particular portfolio
        for asset in desired_portfolio:
            if asset not in broker_portfolio:
                broker_portfolio[asset] = {"quantity": 0}
        for asset in broker_portfolio:
            if asset not in ("total_cash", "total_value", "total_equity"):
                if asset not in desired_portfolio:
                    desired_portfolio[asset] = {"quantity": 0}

        # Loop through the portfolios and create the diff portfolio
        diff_portfolio = {}
        for asset in desired_portfolio:
            des_qty = desired_portfolio[asset]["quantity"]
            brk_qty = broker_portfolio[asset]["quantity"]
            order_qty = des_qty - brk_qty
            diff_portfolio[asset] = {"quantity": order_qty}

        # Create the final Order list from the diff portfolio
        final_order_list = [
            Order(
                self.cur_dt, asset,
                diff_portfolio[asset]["quantity"]
            )
            for asset, asset_dict in sorted(
                diff_portfolio.items(), key=lambda x: x[0].symbol
            )
            if diff_portfolio[asset]["quantity"] != 0
        ]
        return final_order_list

    def _is_rebalance_event(self):
        """
        If there are no rebalance times provided then assume rebalancing
        on every event.

        If rebalance times are provided then only rebalance if the current
        time, as far as the PCM is concerned, is found in the list of
        specified rebalance times.
        """
        if self.rebalance_times is None or self.rebalance_times == []:
            return True
        if self.cur_dt in self.rebalance_times:
            return True
        return False

    def update(self, dt):
        """
        Update the PortfolioConstructionModel's current time.
        """
        if dt < self.cur_dt:
            raise PortfolioConstructionModelException(
                'Cannot update PortfolioConstructionModel current time '
                'of "%s" as new time of "%s" is in the past.' % (
                    self.cur_dt, dt
                )
            )
        else:
            self.cur_dt = dt

    def generate_orders(self, forecasts):
        """
        Takes in a list of Forecast instances and checks them for
        validity.

        Creates an initial 'alpha' portfolio, based on these Forecasts,
        passing it through the RiskModel and TransactionCostModel
        to potentially modify Orders deemed risky or expensive.

        Obtain the latest brokerage portfolio, compare it to the
        desired portfolio and produce a list of necessary Orders.
        """
        if self._check_all_forecasts(forecasts):
            self.forecasts = forecasts

        # Only calculate portfolio logic if rebalancing is necessary
        if self._is_rebalance_event():
            # Generate the desired portfolio
            alpha_portfolio = self._construct_desired_alpha_portfolio()
            risk_portfolio = self._construct_desired_risk_portfolio(
                alpha_portfolio
            )
            desired_portfolio = self._construct_desired_trans_cost_portfolio(
                risk_portfolio
            )

            # Obtain latest broker portfolio and create diff Order list
            broker_portfolio = self.broker.get_portfolio_as_dict(
                self.broker_portfolio_id
            )
            order_list = self._diff_desired_broker_portfolios(
                desired_portfolio, broker_portfolio
            )      
            return order_list
        else:
            return []
