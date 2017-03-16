from .position import Position

class IBPortfolio(object):
    def __init__(self, ib_service, price_handler, cash):
        """
        On creation, the IB Portfolio will request all current portfolio details
        from the IB API.

        WORK PROCESS:
            * Subclass the existing Portfolio implementation, override init() only
            * Bootstrap the portfolio by requesting current positions from IB
            * Decide where we handle OrderStatus() events (guessing ExecutionHandler)
        """
        self.price_handler = price_handler
        self.ib_service = ib_service

        self.init_cash = cash
        self.equity = cash
        self.cur_cash = cash
        self.positions = {}
        self.closed_positions = []  # ???
        self.realised_pnl = 0

        # Request portfolio updates
        self.ib_service.reqAccountUpdates(True, "")

    def _update_portfolio(self):
        """
        TODO needs to have listeners or notifications from:
            * self.ib_service.updateAccountValue()
            * self.ib_service.updatePortfolio()
        Does this also need stubbing, if we're only updating based on IB Callbacks?
        """
        pass

    def _add_position(
        self, action, ticker,
        quantity, price, commission
    ):
        """
        TODO I believe should be handled from _update_portfolio iff a new position
        comes through from IB's callback.
        """
        pass

    def _modify_position(
        self, action, ticker,
        quantity, price, commission
    ):
        """
        TODO I believe should be handled from _update_portfolio if a position
        quantity changes between IB callbacks.
        """
        pass


    def transact_position(
        self, action, ticker,
        quantity, price, commission
    ):
        """
        TODO: Does this need stubbing if we'll be updating positions on the
        IBService updatePortfolio() callback?
        """
        pass
