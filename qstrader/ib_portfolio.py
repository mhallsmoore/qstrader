import time
from .position import Position
from .portfolio import Portfolio

class IBPortfolio(Portfolio):
    def __init__(self, ib_service, price_handler, cash):
        """
        On creation, the IB Portfolio will request all current portfolio details
        from the IB API.

        WORK PROCESS:
            * Subclass the existing Portfolio implementation, override init() only
            * Bootstrap the portfolio by requesting current positions from IB
            * Decide where we handle OrderStatus() events (guessing ExecutionHandler)
        """
        Portfolio.__init__(self, price_handler, cash)
        self.ib_service = ib_service

        # Bootstrap the portfolio by loading data from IB.
        self.ib_service.reqAccountUpdates(True, "")
        time.sleep(5)  # Ugly, but no way to implement future/promise with IB's response?
        while not self.ib_service.portfolioUpdatesQueue.empty():
            # Create the position
            portfolioUpdate = self.ib_service.portfolioUpdatesQueue.get(False)
            contract = portfolioUpdate[0]
            contract.exchange = contract.primaryExchange
            position = Position(
                "BOT" if portfolioUpdate[1] > 0 else "SLD",
                contract.symbol, portfolioUpdate[1], 0, 0, 0, 0
            )
            # Override some of the position variables
            if portfolioUpdate[1] > 0:
                position.buys = portfolioUpdate[1]  ## TODO Confirm correct
            else:
                position.sells = portfolioUpdate[1] ## TODO Confirm correct
            position.quantity = portfolioUpdate[1]
            position.init_price = portfolioUpdate[4]
            position.realised_pnl = portfolioUpdate[6]
            position.unrealized_pnl = portfolioUpdate[5]
            position.market_value = portfolioUpdate[3]

            # Add the position to the QSTrader portfolio
            self.positions[contract.symbol] = position

            # Subscribe the PriceHandler to this position so we get updates on value.
            self.price_handler._subscribe_contract(contract)
