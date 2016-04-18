from abc import ABCMeta, abstractmethod

from qstrader.event.event import SignalEvent


class Strategy(object):
    """
    Strategy is an abstract base class providing an interface for
    all subsequent (inherited) strategy handling objects.

    The goal of a (derived) Strategy object is to generate Signal
    objects for particular symbols based on the inputs of ticks 
    generated from a PriceHandler (derived) object.

    This is designed to work both with historic and live data as
    the Strategy object is agnostic to data location.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_signals(self, event):
        """
        Provides the mechanisms to calculate the list of signals.
        """
        raise NotImplementedError("Should implement calculate_signals()")


class TestStrategy(Strategy):
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
        if event.type == 'TICK' and event.ticker == ticker:
            if self.ticks % 5 == 0:
                if self.invested == False:
                    signal = SignalEvent(ticker, "BOT")
                    self.events_queue.put(signal)
                    self.invested = True
                else:
                    signal = SignalEvent(ticker, "SLD")
                    self.events_queue.put(signal)
                    self.invested = False
            self.ticks += 1


class BuyAndHoldStrategy(Strategy):
    """
    A testing strategy that simply purchases (longs) a set of
    assets upon first receipt of the relevant tick event and 
    then holds until the completion of a backtest.
    """
    def __init__(self, tickers, events_queue):
        self.tickers = tickers
        self.events_queue = events_queue
        self.ticks = 0
        self.invested = False

    def calculate_signals(self, event):
        ticker = self.tickers[0]
        if event.type == "TICK" and event.ticker == ticker:
            if not self.invested and self.ticks == 0:
                signal = SignalEvent(ticker, "BOT")
                self.events_queue.put(signal)
                self.invested = True
            self.ticks += 1
