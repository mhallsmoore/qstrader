import calendar
import datetime
from math import floor

from qstrader import settings
from qstrader.strategy.base import AbstractStrategy
from qstrader.position_sizer.base import AbstractPositionSizer
from qstrader.event import SignalEvent, EventType
from qstrader.compat import queue
from qstrader.trading_session.backtest import Backtest
from qstrader.price_parser import PriceParser


class LiquidateRebalancePositionSizer(AbstractPositionSizer):
    """
    Carries out a periodic full liquidation and rebalance of
    the Portfolio.

    This is achieved by determining whether an order type type
    is "EXIT" or "BOT/SLD".

    If the former, the current quantity of shares in the ticker
    is determined and then BOT or SLD to net the position to zero.

    If the latter, the current quantity of shares to obtain is
    determined by prespecified weights and adjusted to reflect
    current account equity.
    """
    def __init__(self, ticker_weights):
        self.ticker_weights = ticker_weights

    def size_order(self, portfolio, initial_order):
        """
        Size the order to reflect the dollar-weighting of the
        current equity account size based on pre-specified
        ticker weights.
        """
        ticker = initial_order.ticker
        if initial_order.action == "EXIT":
            # Obtain current quantity and liquidate
            cur_quantity = portfolio.positions[ticker].quantity
            if cur_quantity > 0:
                initial_order.action = "SLD"
                initial_order.quantity = cur_quantity
            elif cur_quantity < 0:
                initial_order.action = "BOT"
                initial_order.quantity = cur_quantity
            else:
                initial_order.quantity = 0
        else:
            weight = self.ticker_weights[ticker]
            # Determine total portfolio value, work out dollar weight
            # and finally determine integer quantity of shares to purchase
            price = portfolio.price_handler.tickers[ticker]["adj_close"]
            price /= PriceParser.PRICE_MULTIPLIER
            equity = portfolio.equity / PriceParser.PRICE_MULTIPLIER
            dollar_weight = weight * equity
            weighted_quantity = int(floor(dollar_weight / price))
            # Update quantity
            initial_order.quantity = weighted_quantity
        return initial_order


class MonthlyLiquidateRebalanceStrategy(AbstractStrategy):
    """
    A generic strategy that allows monthly rebalancing of a
    set of tickers, via full liquidation and dollar-weighting
    of new positions.

    Must be used in conjunction with the
    LiquidateRebalancePositionSizer object to work correctly.
    """
    def __init__(self, tickers, events_queue):
        self.tickers = tickers
        self.events_queue = events_queue
        self.tickers_invested = self._create_invested_list()

    def _end_of_month(self, cur_time):
        """
        Determine if the current day is at the end of the month.
        """
        cur_day = cur_time.day
        end_day = calendar.monthrange(cur_time.year, cur_time.month)[1]
        return cur_day == end_day

    def _create_invested_list(self):
        """
        Create a dictionary with each ticker as a key, with
        a boolean value depending upon whether the ticker has
        been "invested" yet. This is necessary to avoid sending
        a liquidation signal on the first allocation.
        """
        tickers_invested = {ticker: False for ticker in self.tickers}
        return tickers_invested

    def calculate_signals(self, event):
        """
        For a particular received BarEvent, determine whether
        it is the end of the month (for that bar) and generate
        a liquidation signal, as well as a purchase signal,
        for each ticker.
        """
        if (
            event.type in [EventType.BAR, EventType.TICK] and
            self._end_of_month(event.time)
        ):
            ticker = event.ticker
            if self.tickers_invested[ticker]:
                liquidate_signal = SignalEvent(ticker, "EXIT")
                self.events_queue.put(liquidate_signal)
            long_signal = SignalEvent(ticker, "BOT")
            self.events_queue.put(long_signal)
            self.tickers_invested[ticker] = True


def run(config, testing, tickers, filename):
    # Backtest information
    title = ['Monthly Liquidate/Rebalance on 60%/40% SPY/AGG Portfolio']
    initial_equity = 500000.0
    start_date = datetime.datetime(2006, 11, 1)
    end_date = datetime.datetime(2016, 10, 12)

    # Use the Monthly Liquidate And Rebalance strategy
    events_queue = queue.Queue()
    strategy = MonthlyLiquidateRebalanceStrategy(
        tickers, events_queue
    )

    # Use the liquidate and rebalance position sizer
    # with prespecified ticker weights
    ticker_weights = {
        "SPY": 0.6,
        "AGG": 0.4,
    }
    position_sizer = LiquidateRebalancePositionSizer(
        ticker_weights
    )

    # Set up the backtest
    backtest = Backtest(
        config, strategy, tickers,
        initial_equity, start_date, end_date,
        events_queue, position_sizer=position_sizer,
        title=title, benchmark=tickers[0],
    )
    results = backtest.simulate_trading(testing=testing)
    return results


if __name__ == "__main__":
    # Configuration data
    testing = False
    config = settings.from_file(
        settings.DEFAULT_CONFIG_FILENAME, testing
    )
    tickers = ["SPY", "AGG"]
    filename = None
    run(config, testing, tickers, filename)
