class ExecutionHandler(object):
    """
    Handles the execution of a list of Orders output by the
    PortfolioConstructionModel via the Broker.

    Parameters
    ----------
    broker : `Broker`
        The derived Broker instance to execute orders against.
    broker_portfolio_id : `str`
        The specific portfolio at the Broker to execute against.
    universe : `Universe`
        The derived Universe instance to obtain the Asset list from.
    submit_orders : `Boolean`, optional
        Whether to actually submit orders to the Broker or silently
        discard them. Defaults to False -> Do not send orders.
    execution_algo : `ExecutionAlgorithm`, optional
        The derived ExecutionAlgorithm instance to use for the
        execution strategy.
    data_handler : `DataHandler`, optional
        The derived DataHandler instances used to (optionally) obtain any
        necessary data for the execution strategy.
    """

    def __init__(
        self,
        broker,
        broker_portfolio_id,
        universe,
        submit_orders=False,
        execution_algo=None,
        data_handler=None
    ):
        self.broker = broker
        self.broker_portfolio_id = broker_portfolio_id
        self.universe = universe
        self.submit_orders = submit_orders
        self.execution_algo = execution_algo
        self.data_handler = data_handler

    def _apply_execution_algo_to_rebalances(self, dt, rebalance_orders):
        """
        Generates a new list of Orders based on the appropriate
        execution strategy.

        Parameters
        ----------
        dt : `pd.Timestamp`
            The current time used to populate the Order instances.
        rebalance_orders : `list[Order]`
            The list of rebalance orders to execute.

        Returns
        -------
        `list[Order]`
            The final list of orders to send to the Broker to be executed.
        """
        return self.execution_algo(dt, rebalance_orders)

    def __call__(self, dt, rebalance_orders):
        """
        Take the list of rebalanced Orders generated from the
        portfolio construction process and execute them at the
        Broker, via the appropriate execution algorithm.

        Parameters
        ----------
        dt : `pd.Timestamp`
            The current time used to populate the Order instances.
        rebalance_orders : `list[Order]`
            The list of rebalance orders to execute.

        Returns
        -------
        `None`
        """
        final_orders = self._apply_execution_algo_to_rebalances(
            dt, rebalance_orders
        )

        # If order submission is specified then send the
        # individual order items to the Broker instance
        if self.submit_orders:
            for order in final_orders:
                self.broker.submit_order(self.broker_portfolio_id, order)
