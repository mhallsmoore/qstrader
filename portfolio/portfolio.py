from decimal import Decimal
from qstrader.position.position import Position


class Portfolio(object):
    def __init__(self, price_handler, cash):
        self.price_handler = price_handler
        self.init_cash = cash
        self.cur_cash = cash
        self.positions = {}
        self._reset_values()

    def _reset_values(self):
        self.cur_cash = self.init_cash
        self.equity = self.cur_cash
        self.unrealised_pnl = Decimal('0.00')
        self.realised_pnl = Decimal('0.00')

    def _update_portfolio(self):
        for ticker in self.positions:
            pt = self.positions[ticker]
            self.unrealised_pnl += pt.unrealised_pnl
            self.realised_pnl += pt.realised_pnl
            self.cur_cash -= pt.cost_basis
            self.cur_cash += (self.realised_pnl - self.unrealised_pnl)
            self.equity += (
                pt.market_value - pt.cost_basis + self.realised_pnl - self.unrealised_pnl
            )

    def add_position(
        self, action, ticker,
        quantity, price, commission
    ):
        self._reset_values()
        if ticker not in self.positions:
            bid, ask = self.price_handler.get_best_bid_ask(ticker)
            position = Position(
                action, ticker, quantity,
                price, commission, bid, ask
            )
            self.positions[ticker] = position
            self._update_portfolio()
        # Else, do nothing but log or flag this up

    def modify_position(
        self, action, ticker, 
        quantity, price, commission
    ):
        self._reset_values()
        if ticker in self.positions:
            self.positions[ticker].transact_shares(
                action, quantity, price, commission
            )
            bid, ask = self.price_handler.get_best_bid_ask(ticker)
            self.positions[ticker].update_market_value(bid, ask)
            self._update_portfolio()
        else:
            print("Ticker %s not in the current position list." % ticker)
