from .base import AbstractStrategy

from ..event import (SignalEvent, EventType)


class ExampleStrategy(AbstractStrategy):
    """
    A testing strategy that alternates between buying and selling
    a ticker on every 5th tick. This has the effect of continuously
    "crossing the spread" and so will be loss-making strategy.

    It is used to test that the backtester/live trading system is
    behaving as expected.
    """
    def __init__(self, tickers, events_queue):
        self.tickers = tickers
        self.events_queue = events_queue
        self.ticks = 0
        self.invested = False

    def calculate_signals(self, event):
        ticker = self.tickers[0]
        if event.type == EventType.TICK and event.ticker == ticker:
            if self.ticks % 5 == 0:
                if not self.invested:
                    signal = SignalEvent(ticker, "BOT")
                    self.events_queue.put(signal)
                    self.invested = True
                else:
                    signal = SignalEvent(ticker, "SLD")
                    self.events_queue.put(signal)
                    self.invested = False
            self.ticks += 1
