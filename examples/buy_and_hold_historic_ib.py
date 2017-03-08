import datetime

from qstrader import settings
from qstrader.strategy.base import AbstractStrategy
from qstrader.event import SignalEvent, EventType
from qstrader.compat import queue
from qstrader.trading_session.backtest import Backtest
from qstrader.service.ib import IBService
from qstrader.price_handler.ib_bar import IBBarPriceHandler

class BuyAndHoldStrategy(AbstractStrategy):
    """
    A testing strategy that simply purchases (longs) any asset that
    matches what was passed in on initialization and
    then holds until the completion of a backtest.
    """
    def __init__(
        self, tickers, events_queue,
        base_quantity=100
    ):
        self.tickers = tickers
        self.invested = dict.fromkeys(tickers)
        self.events_queue = events_queue
        self.base_quantity = base_quantity

    def calculate_signals(self, event):
        if (
            event.type in [EventType.BAR, EventType.TICK] and
            event.ticker in self.tickers
        ):
            if not self.invested[event.ticker]:
                signal = SignalEvent(
                    event.ticker, "BOT",
                    suggested_quantity=self.base_quantity
                )
                self.events_queue.put(signal)
                self.invested[event.ticker] = True


def run(config, testing, tickers, filename):
    # Backtest information
    title = ['Buy and Hold Example on %s' % tickers[0]]
    initial_equity = 10000.0
    start_date = datetime.datetime(2000, 1, 1)
    end_date = datetime.datetime(2014, 1, 1)
    events_queue = queue.Queue()

    # Set up IBService
    ib_service = IBService()
    ib_service.connect("127.0.0.1", 4001, 0) # TODO from config
    ib_service.start()

    # Set up the IB PriceHandler
    price_handler = IBBarPriceHandler(
        ib_service, events_queue, tickers, config
    )

    # Use the Buy and Hold Strategy
    strategy = BuyAndHoldStrategy(tickers, events_queue)

    # Set up the backtest
    backtest = Backtest(
        config, strategy, tickers,
        initial_equity, start_date, end_date,
        events_queue, price_handler, title=title
    )
    results = backtest.simulate_trading(testing=testing)

    # Disconnect from services
    ib_service.stop_event.set()
    ib_service.join()

    return results


if __name__ == "__main__":
    # Configuration data
    testing = False
    config = settings.from_file(
        settings.DEFAULT_CONFIG_FILENAME, testing
    )
    tickers = ["CBA", "BHP", "STO", "FMG", "WOW", "WES"]
    filename = None
    run(config, testing, tickers, filename)
