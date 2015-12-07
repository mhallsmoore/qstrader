import deepcopy


class Portfolio(object):
    def __init__(self):
        self.positions = {}

    def update_portfolio_prices(self, price_handler):
        pass

    def delta_to_portfolio(self, portfolio):
        pass

    def delta_from_portfolio(self, portfolio):
        pass

    def portfolio_from_fill(self, fill, bid, ask, inplace=False):
        if inplace:
            if fill.ticker in self.positions:
                # Decide whether to add, remove or close
                pass
            else:
                self.positions[fill.ticker] = Position(
                    fill, bid, ask
                )
            return None  # Inplace
        else:
            new_portfolio = copy.deepcopy(self)
            if fill.ticker in new_portfolio.positions:
                # Decide whether to add, remove or close
                pass
            else:
                new_portfolio.positions[fill.ticker] = Position(
                    fill, bid, ask
                )
            return new_portfolio

    def portfolio_from_signal(self, signal, bid, ask, inplace=False):
        # Create a false "Fill" and then use portfolio_from_fill
        false_fill = FillEvent(...)
        if inplace:
            self.portfolio_from_fill(
                false_fill, bid, ask, inplace=True
            )
            return None
        else:
            new_portfolio = self.portfolio_from_fill(
                false_fill, bid, ask, inplace=False
            )
            return new_portfolio


class PortfolioHandler(object):
    def __init__(
        self, event_queue, price_handler, 
        risk_handler, execution_handler
    ):
        self.event_queue = event_queue
        self.price_handler = price_handler
        self.risk_handler = risk_handler
        self.execution_handler = execution_handler
        self.current_portfolio = Portfolio()

    def _update_portfolio(self, market):
        pass

    def on_market_event(self, market):
        pass

    def on_signal_event(self, signal):
        # Construct new desired portfolio from signal

        # Send desired portfolio to risk layer

        # Risk layer amends desired portfolio and returns

        # Create "delta" trades from old to new portfolio

        # Send these "delta" trades to execution handler
        # -> Also store order information in database

        pass

    def on_fill_event(self, fill):
        # Check if position exists for fill
        # -> If not, create a new position with fill information
        # -> Otherwise, update current position with new fill information
        # Store fill information in DB
        # Update all market prices
        pass
