import copy
from decimal import Decimal, ROUND_HALF_DOWN


TWOPLACES = Decimal("0.01")
FIVEPLACES = Decimal("0.00001")


class Position(object):
    def __init__(
        self, action, ticker, init_quantity, 
        init_price, init_commission, 
        bid, ask
    ):
        self.action = action
        self.ticker = ticker
        self.quantity = init_quantity
        self.init_price = init_price
        self.init_commission = init_commission
        
        self.realised_pnl = Decimal("0.00")
        self.unrealised_pnl = Decimal("0.00")

        self.buys = Decimal("0")
        self.sells = Decimal("0")
        self.avg_bot = Decimal("0.00")
        self.avg_sld = Decimal("0.00")
        self.total_bot = Decimal("0.00")
        self.total_sld = Decimal("0.00")
        self.total_commission = init_commission

        self._calculate_initial_value()
        self.update_market_value(bid, ask)

    def _calculate_initial_value(self):
        if self.action == "BOT":
            self.buys = self.quantity
            self.avg_bot = self.init_price.quantize(FIVEPLACES)
            self.total_bot = (self.buys * self.avg_bot).quantize(TWOPLACES)
            self.avg_price = (
                (self.init_price * self.quantity + self.init_commission)/self.quantity
            ).quantize(FIVEPLACES)
            self.cost_basis = (
                self.quantity * self.avg_price
            ).quantize(TWOPLACES)
        else:  # action == "SLD"
            self.sells = self.quantity
            self.avg_sld = self.init_price.quantize(FIVEPLACES)
            self.total_sld = (self.sells * self.avg_sld).quantize(TWOPLACES)
            self.avg_price = (
                (self.init_price * self.quantity - self.init_commission)/self.quantity
            ).quantize(FIVEPLACES)
            self.cost_basis = (
                -self.quantity * self.avg_price
            ).quantize(TWOPLACES)
        self.net = self.buys - self.sells
        self.net_total = (self.total_sld - self.total_bot).quantize(TWOPLACES)
        self.net_incl_comm = (self.net_total - self.init_commission).quantize(TWOPLACES)

    def update_market_value(self, bid, ask):
        midpoint = (bid+ask)/Decimal("2.0")
        self.market_value = (
            self.quantity * midpoint
        ).quantize(TWOPLACES)
        self.unrealised_pnl = (
            self.market_value - self.cost_basis
        ).quantize(TWOPLACES)
        self.realised_pnl = (
            self.market_value + self.net_incl_comm
        )

    def transact_shares(self, action, quantity, price, commission):
        prev_quantity = self.quantity
        prev_commission = self.total_commission

        self.total_commission += commission
        
        # Adjust total bought and sold
        if action == "BOT":            
            self.avg_bot = (
                (self.avg_bot*self.buys + price*quantity)/(self.buys + quantity)
            ).quantize(FIVEPLACES)
            if self.action != "SLD":
                self.avg_price = (
                    (
                        self.avg_price*self.buys + 
                        price*quantity+commission
                    )/(self.buys + quantity)
                ).quantize(FIVEPLACES)
            self.buys += quantity
            self.total_bot = (self.buys * self.avg_bot).quantize(TWOPLACES)

        # action == "SLD"
        else:  
            self.avg_sld = (
                (self.avg_sld*self.sells + price*quantity)/(self.sells + quantity)
            ).quantize(FIVEPLACES)
            if self.action != "BOT":
                self.avg_price = (
                    (
                        self.avg_price*self.sells + 
                        price*quantity-commission
                    )/(self.sells + quantity)
                ).quantize(FIVEPLACES)
            self.sells += quantity
            self.total_sld = (self.sells * self.avg_sld).quantize(TWOPLACES)

        # Adjust net values, including commissions
        self.net = self.buys - self.sells
        
        self.quantity = self.net
        self.net_total = (
            self.total_sld - self.total_bot
        ).quantize(TWOPLACES)
        self.net_incl_comm = (
            self.net_total - self.total_commission
        ).quantize(TWOPLACES)

        # Adjust average price and cost basis
        self.cost_basis = (
            self.quantity * self.avg_price
        ).quantize(TWOPLACES)
