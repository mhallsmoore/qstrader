from position.position import Position


class Portfolio(object):
    def __init__(self, price_handler, cash):
        self.price_handler
        self.cash = cash
        self.positions = {}
        self._reset_values()

    def _reset_values(self):
        self.equity = self.cash
        self.unrealised_pnl = Decimal('0.00')
        self.realised_pnl = Decimal('0.00')

    def add_position(
        self, action, ticker,
        quantity, price, commission
    ):
        if ticker not in self.positions:
            bid, ask = self.price_handler.get_best_bid_ask(ticker)
            position = Position(
                action, ticker, quantity,
                price, commission, bid, ask
            )
            self.positions[ticker] = position
        # Else, do nothing but log or flag this up

    def update_portfolio(self):
        self._reset_values()
        for p in self.positions:
            bid, ask = self.price_handler.get_best_bid_ask(p)
            self.positions[p].update_market_value(bid, ask)
            self.equity += self.positions[p].market_value
            self.unrealised_pnl += self.positions[p].unrealised_pnl
            self.realised_pnl += self.positions[p].realised_pnl
        self.equity += (self.unrealised_pnl + self.realised_pnl)