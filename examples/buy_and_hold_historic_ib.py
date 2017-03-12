import datetime

from qstrader import settings
from qstrader.strategy.base import AbstractStrategy
from qstrader.event import SignalEvent, EventType
from qstrader.compat import queue
from qstrader.trading_session import TradingSession
from qstrader.service.ib import IBService
from qstrader.price_handler.ib_bar import IBBarPriceHandler
from ibapi.contract import Contract


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
    title = ['Buy and Hold Historic IB Example']
    initial_equity = 10000.0
    events_queue = queue.Queue()

    # Set up IBService
    ib_service = IBService()
    ib_service.connect("127.0.0.1", 4001, 0)  # TODO from config
    ib_service.start()

    # Set up IB Contract objects for the PriceHandler
    # MORE INFO: https://www.interactivebrokers.com/en/?f=%2Fen%2Fgeneral%2Fcontact%2FtipsContractsDatabaseSearch.php%3Fib_entity%3Dllc
    symbols = ["CBA", "BHP", "STO", "FMG", "WOW", "WES"]
    contracts = []
    for symbol in symbols:
        contract = Contract()
        contract.exchange = "SMART"
        contract.symbol = symbol
        contract.secType = "STK"
        contract.currency = "AUD"
        contracts.append(contract)

    # Set up the IB PriceHandler. Want 5 day's of minute bars, up to yesterday.
    # Look at IB Documentation for possible values.
    end_date = datetime.datetime.now() - datetime.timedelta(days=1)
    price_handler = IBBarPriceHandler(
        ib_service, events_queue, contracts, config,
        "historic", end_date, hist_duration="5 D", hist_barsize="1 min"
    )

    # Use the Buy and Hold Strategy
    strategy = BuyAndHoldStrategy(tickers, events_queue)

    # Start/End TODO redundant -- only required for default (Yahoo) price handler.
    start_date = datetime.datetime(2000, 1, 1)
    end_date = datetime.datetime(2014, 1, 1)

    # Set up the backtest
    backtest = TradingSession(
        config, strategy, tickers,
        initial_equity, start_date, end_date,
        events_queue, price_handler=price_handler, title=title
    )
    results = backtest.start_trading(testing=testing)

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
