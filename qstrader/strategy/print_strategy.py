from qstrader.strategy.strategy import Strategy


class PrintStrategy(Strategy):
    """
    A print strategy that only print TICK and BAR
    """
    def __init__(self, tickers, events_queue):
        self.tickers = tickers
        self.events_queue = events_queue
        self.ticks = 0
        self.bars = 0

    def calculate_signals(self, event):
        if event.ticker in self.tickers:
            if event.type == 'TICK':
                print("%s %d, at %s" % (event.type, self.ticks, event.time))
                self.ticks += 1
            elif event.type == 'BAR':
                print("%s %d, at %s" % (event.type, self.bars, event.time))
                print(event)
                self.bars += 1
