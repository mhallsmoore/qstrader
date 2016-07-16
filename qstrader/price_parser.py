from multipledispatch import dispatch
from qstrader import settings

class PriceParser(object):
    """
    PriceParser is designed to abstract away the underlying number used as a price
    within qstrader. Due to efficiency and floating point precision limitations,
    QSTrader uses an integer to represent all prices. This means that $0.10 is,
    internally, 10,000,000. Because such large numbers are rather unwieldy
    for humans, the PriceParser will take "normal" 2dp numbers as input, and show
    "normal" 2dp numbers as output when requested to `display()`

    For consistency's sake, PriceParser should be used for ALL prices that enter
    the qstrader system. Numbers should also always be parsed correctly to view.

    """
    PRICE_MULTIPLIER = 10000000 #10mn

    # Parse
    @staticmethod
    @dispatch(int)
    def parse(x):
        return x

    @staticmethod
    @dispatch(float)
    def parse(x):
        return int(x * PriceParser.PRICE_MULTIPLIER)

    # Display
    @staticmethod
    @dispatch(int)
    def display(x):
        return str(x / PriceParser.PRICE_MULTIPLIER)

    @staticmethod
    @dispatch(float)
    def display(x):
        return str(x)
