from qstrader.portfolio.portfolio import Portfolio


class PortfolioHandler(object):
    def __init__(
        self, initial_cash, events_queue, 
        price_handler, risk_manager
    ):
        """
        The PortfolioHandler is designed to interact with the 
        backtesting or live trading overall event-driven
        architecture. It exposes two methods, on_signal and
        on_fill, which handle how SignalEvent and FillEvent
        objects are dealt with.

        Each PortfolioHandler contains a Portfolio object,
        which stores the actual Position objects. The
        PortfolioHandler also takes a handle to the RiskManager,
        which is used to modify any generated orders to remain
        in line with risk parameters.
        """
        self.initial_cash = initial_cash
        self.events_queue = events_queue
        self.price_handler = price_handler
        self.risk_manager = risk_manager
        self.portfolio = Portfolio(price_handler, initial_cash)

    def _form_orders_from_signal(self, signal_event):
        """
        Take a SignalEvent object and use it to form a list
        of order objects. These are not OrderEvent objects,
        as they have yet to be sent to the RiskManager object.
        At this stage they are simply "suggestions" that the
        RiskManager will either verify, modify or eliminate.
        """
        return orders

    def _place_orders_onto_queue(self, order_list):
        """
        Once the RiskManager has verified, modified or eliminated
        any order objects, they are placed onto the events queue,
        to ultimately be executed by the ExecutionHandler.
        """
        for order_event in order_list:
            self.events_queue.put(order_event)

    def _convert_fill_to_portfolio_update(self, fill_event):
        """
        Upon receipt of a FillEvent, the PortfolioHandler converts
        the event into a transaction that gets stored in the Portfolio
        object. This ensures that the broker and the local portfolio
        are "in sync".

        In addition, for backtesting purposes, the portfolio value can
        be reasonably estimated in a realistic manner, simply by 
        modifying how the ExecutionHandler object handles slippage,
        transaction costs, liquidity and market impact.
        """
        pass

    def on_signal(self, signal_event):
        """
        This is called by the backtester or live trading architecture
        to form the initial orders from the SignalEvent. These orders
        are then sent to the RiskManager to verify, modify or eliminate.

        Once received from the RiskManager they are converted into
        full OrderEvent objects and sent back to the events queue.
        """
        # Create the initial order list from a signal event
        initial_orders = self._form_orders_from_signal(signal_event)
        # Refine or eliminate the orders via the risk manager overlay
        order_events = self.risk_manager.refine_orders(
            portfolio, initial_orders
        )
        # Place orders onto events queue
        self._place_orders_onto_queue(order_events)

    def on_fill(self, fill_event):
        """
        This is called by the backtester or live trading architecture
        to take a FillEvent and update the Portfolio object with new
        or modified Positions.

        In a backtesting environment these FillEvents will be simulated
        by a model representing the execution, whereas in live trading
        they will come directly from a brokerage (such as Interactive
        Brokers).
        """
        self._convert_fill_to_portfolio_update(fill_event)