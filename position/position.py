import copy
from decimal import Decimal, ROUND_HALF_DOWN


TWOPLACES = Decimal("0.01")
FIVEPLACES = Decimal("0.00001")


class Position(object):
    def __init__(self, fill, bid, ask):
        self.ticker = fill.ticker
        self.side = fill.side
        self.quantity = fill.quantity

        # Calculate initial values and update prices
        self._calculate_initial_value(fill)
        self.update_position_prices(bid, ask)
        
    def _calculate_initial_value(self, fill):
        self.avg_price = (
            (fill.price * fill.quantity + fill.commission)/self.quantity
        ).quantize(FIVEPLACES)
        self.cost_basis = (
            self.quantity * self.avg_price
        ).quantize(TWOPLACES)

    def update_position_prices(self, bid, ask):
        # Update market bid and ask price
        self.bid = bid
        self.ask = ask

        # Calculate market price depending on trade side
        if self.side == "LONG":
            self.market_price = self.bid
        else:
            self.market_price = self.ask

        # Calculate market value and unrealised profit & loss
        self.market_value = (
            self.quantity * self.market_price
        ).quantize(TWOPLACES)
        self.abs_unrealized_pnl = (
            self.market_value - self.cost_basis
        ).quantize(TWOPLACES)
        self.per_unrealized_pnl = (
            (
                self.abs_unrealized_pnl/self.cost_basis
            ).quantize(FIVEPLACES) * Decimal("100.00")
        ).quantize(TWOPLACES)

    def buy_shares(self, fill, bid, ask):
        old_quantity = copy.deepcopy(self.quantity)
        self.quantity += fill.quantity
        old_cost_basis = self.avg_price * old_quantity
        new_cost_basis = fill.price * fill.quantity + fill.commission

        # Update average price and cost basis
        self.avg_price = (
            (old_cost_basis + new_cost_basis)/self.quantity
        ).quantize(TWOPLACES)
        self.cost_basis = (
            self.quantity * self.avg_price
        ).quantize(TWOPLACES)

        # Update market value and PnL
        self.update_position_prices(bid, ask)

    """
    def sell_shares(self, fill, bid, ask):
        pass

    def close_position(self, fill):
        pass
    """
    