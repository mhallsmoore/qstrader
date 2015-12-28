from decimal import Decimal
import pprint

from qstrader.portfolio.portfolio import Portfolio


class PriceHandlerMock(object):
    def __init__(self):
        pass

    def get_best_bid_ask(self, ticker):
        prices = {
            "GOOG": (Decimal("762.15"), Decimal("762.15")),
            "AMZN": (Decimal("660.51"), Decimal("660.51")),
        }
        return prices[ticker]


ph = PriceHandlerMock()
cash = Decimal("500000.00")
port = Portfolio(ph, cash)

port.add_position("BOT", "GOOG", 100, Decimal("761.75"), Decimal("1.00"))
port.add_position("BOT", "AMZN", 100, Decimal("660.86"), Decimal("1.00"))
port.modify_position("BOT", "AMZN", 100, Decimal("660.14"), Decimal("1.00"))
port.modify_position("BOT", "AMZN", 150, Decimal("660.20"), Decimal("1.00"))
port.modify_position("SLD", "AMZN", 300, Decimal("659.713"), Decimal("1.50"))

print("CASH:", port.cur_cash)
print("EQUITY:", port.equity)
print("UPnL:", port.unrealised_pnl)
print("PnL:", port.realised_pnl)
pprint.pprint(port.positions)
print("")

for p in port.positions:
    print("AVG PRICE:", port.positions[p].avg_price)
    print("COST BASIS:", port.positions[p].cost_basis)
    print("MARKET VALUE:", port.positions[p].market_value)
    print("UNREALISED PNL:", port.positions[p].unrealised_pnl)
    print("REALISED PNL:", port.positions[p].realised_pnl)
    print("")
