from qstrader.execution.execution_handler import (
    ExecutionHandler
)
from qstrader.execution.execution_algo.market_order import (
    MarketOrderExecutionAlgorithm
)
from qstrader.portcon.pcm import (
    PortfolioConstructionModel
)
from qstrader.portcon.optimiser.fixed_weight import (
    FixedWeightPortfolioOptimiser
)
from qstrader.portcon.order_sizer.dollar_weighted import (
    DollarWeightedCashBufferedOrderSizeGeneration
)


class QuantTradingSystem(object):
    """
    Encapsulates all components associated with the quantitative
    trading system. This includes the alpha model(s), the risk
    model, the transaction cost model along with portfolio construction
    and execution mechanism.

    Parameters
    ----------
    universe : `Universe`
        The Asset Universe.
    broker : `Broker`
        The Broker to execute orders against.
    broker_portfolio_id : `str`
        The specific broker portfolio to send orders to.
    data_handler : `DataHandler`
        The data handler instance used for all market/fundamental data.
    alpha_model : `AlphaModel`
        The alpha model used within the portfolio construction.
    risk_model : `AlphaModel`, optional
        An optional risk model used within the portfolio construction.
    cash_buffer_percentage : `float`, optional
        The percentage of the portfolio to retain in cash.
    submit_orders : `Boolean`, optional
        Whether to actually submit generated orders. Defaults to no submission.
    """

    def __init__(
        self,
        universe,
        broker,
        broker_portfolio_id,
        data_handler,
        alpha_model,
        risk_model=None,
        cash_buffer_percentage=0.05,
        submit_orders=False
    ):
        self.universe = universe
        self.broker = broker
        self.broker_portfolio_id = broker_portfolio_id
        self.data_handler = data_handler
        self.alpha_model = alpha_model
        self.risk_model = risk_model
        self.cash_buffer_percentage = cash_buffer_percentage
        self.submit_orders = submit_orders
        self._initialise_models()

    def _initialise_models(self):
        """
        Initialise the various models for the quantitative
        trading strategy. This includes the portfolio
        construction and the execution.

        TODO: Add TransactionCostModel
        TODO: Ensure this is dynamically generated from config.
        """
        # Portfolio Construction
        order_sizer = DollarWeightedCashBufferedOrderSizeGeneration(
            self.broker,
            self.broker_portfolio_id,
            self.data_handler,
            cash_buffer_percentage=self.cash_buffer_percentage
        )
        optimiser = FixedWeightPortfolioOptimiser(
            data_handler=self.data_handler
        )
        self.portfolio_construction_model = PortfolioConstructionModel(
            self.broker,
            self.broker_portfolio_id,
            self.universe,
            order_sizer,
            optimiser,
            alpha_model=self.alpha_model,
            risk_model=self.risk_model,
            data_handler=self.data_handler
        )

        # Execution
        execution_algo = MarketOrderExecutionAlgorithm()
        self.execution_handler = ExecutionHandler(
            self.broker,
            self.broker_portfolio_id,
            self.universe,
            submit_orders=self.submit_orders,
            execution_algo=execution_algo,
            data_handler=self.data_handler
        )

    def __call__(self, dt, stats=None):
        """
        Construct the portfolio and (optionally) execute the orders
        with the broker.

        Parameters
        ----------
        dt : `pd.Timestamp`
            The current time.
        stats : `dict`, optional
            An optional statistics dictionary to append values to
            throughout the simulation lifetime.

        Returns
        -------
        `None`
        """
        # Construct the target portfolio
        rebalance_orders = self.portfolio_construction_model(dt, stats=stats)

        # Execute the orders
        self.execution_handler(dt, rebalance_orders)
