from qstrader.order.suggested import SuggestedOrder


class AbstractPortfolioHandler(object):
    def _create_order_from_signal(self, signal_event):
        """
        Take a SignalEvent object and use it to form a
        SuggestedOrder object. These are not OrderEvent objects,
        as they have yet to be sent to the RiskManager object.
        At this stage they are simply "suggestions" that the
        RiskManager will either verify, modify or eliminate.
        """
        if signal_event.suggested_quantity is None:
            quantity = 0
        else:
            quantity = signal_event.suggested_quantity
        order = SuggestedOrder(
            signal_event.ticker,
            signal_event.action,
            quantity=quantity
        )
        return order

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
        action = fill_event.action
        ticker = fill_event.ticker
        quantity = fill_event.quantity
        price = fill_event.price
        commission = fill_event.commission
        # Create or modify the position from the fill info
        self.portfolio.transact_position(
            action, ticker, quantity,
            price, commission
        )

    def on_signal(self, signal_event):
        """
        This is called by the backtester or live trading architecture
        to form the initial orders from the SignalEvent.

        These orders are sized by the PositionSizer object and then
        sent to the RiskManager to verify, modify or eliminate.

        Once received from the RiskManager they are converted into
        full OrderEvent objects and sent back to the events queue.
        """
        raise NotImplementedError("on_signal is not implemented in the base class!")

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
        raise NotImplementedError("on_fill is not implemented in the base class!")

    def update_portfolio_value(self):
        """
        Update the portfolio to reflect current market value as
        based on last bid/ask of each ticker.
        """
        raise NotImplementedError("update_portfolio_value is not implemented in the base class!")
