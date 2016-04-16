from decimal import Decimal
from qstrader.position.position import Position


class Portfolio(object):
    def __init__(self, price_handler, cash):
        """
        On creation, the Portfolio object contains no
        positions and all values are "reset" to the initial
        cash, with no PnL - realised or unrealised.
        """
        self.price_handler = price_handler
        self.init_cash = cash
        self.cur_cash = cash
        self.positions = {}
        self._reset_values()

    def _reset_values(self):
        """
        This is called after every position addition or
        modification. It allows the calculations to be
        carried out "from scratch" in order to minimise
        errors.

        All cash is reset to the initial values and the
        PnL is set to zero.
        """
        self.cur_cash = self.init_cash
        self.equity = self.cur_cash
        self.unrealised_pnl = Decimal('0.00')
        self.realised_pnl = Decimal('0.00')

    def _update_portfolio(self):
        """
        Updates the Portfolio total values (cash, equity,
        unrealised PnL, realised PnL, cost basis etc.) based
        on all of the current ticker values.

        This method is called after every Position modification.
        """
        for ticker in self.positions:
            pt = self.positions[ticker]
            self.unrealised_pnl += pt.unrealised_pnl
            self.realised_pnl += pt.realised_pnl
            self.cur_cash -= pt.cost_basis
            pnl_diff = pt.realised_pnl - pt.unrealised_pnl
            self.cur_cash += pnl_diff
            self.equity += (
                pt.market_value - pt.cost_basis + pnl_diff
            )

    def _add_position(
        self, action, ticker,
        quantity, price, commission
    ):
        """
        Adds a new Position object to the Portfolio. This
        requires getting the best bid/ask price from the
        price handler in order to calculate a reasonable
        "market value".

        Once the Position is added, the Portfolio values
        are updated.
        """
        self._reset_values()
        if ticker not in self.positions:
            bid, ask = self.price_handler.get_best_bid_ask(ticker)
            position = Position(
                action, ticker, quantity,
                price, commission, bid, ask
            )
            self.positions[ticker] = position
            self._update_portfolio()
        else:
            print(
                "Ticker %s is already in the positions list. " \
                "Could not add a new position." % ticker
            )

    def _modify_position(
        self, action, ticker, 
        quantity, price, commission
    ):
        """
        Modifies a current Position object to the Portfolio.
        This requires getting the best bid/ask price from the
        price handler in order to calculate a reasonable
        "market value".

        Once the Position is modified, the Portfolio values
        are updated.
        """
        self._reset_values()
        if ticker in self.positions:
            self.positions[ticker].transact_shares(
                action, quantity, price, commission
            )
            bid, ask = self.price_handler.get_best_bid_ask(ticker)
            self.positions[ticker].update_market_value(bid, ask)
            self._update_portfolio()
        else:
            print(
                "Ticker %s not in the current position list. " \
                "Could not modify a current position." % ticker
            )

    def transact_position(
        self, action, ticker, 
        quantity, price, commission
    ):
        """
        Handles any new position or modification to 
        a current position, by calling the respective
        _add_position and _modify_position methods. 

        Hence, this single method will be called by the 
        PortfolioHandler to update the Portfolio itself.
        """
        if ticker not in self.positions:
            self._add_position(
                action, ticker, quantity, 
                price, commission
            )
        else:
            self._modify_position(
                action, ticker, quantity, 
                price, commission
            )
    
    def create_portfolio_state_dict(self):
        """
        Creates a dictionary containing the best estimated
        market value of all positions within the Portfolio,
        along with the cash and equity amount.
        """
        state_dict = {
            "cash": self.cur_cash,
            "equity": self.equity
        }
        for ticker in self.positions:
            state_dict[ticker] = self.positions[ticker].market_value
        return state_dict