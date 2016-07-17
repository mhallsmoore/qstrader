from multipledispatch import dispatch


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

    # 10,000,000
    PRICE_MULTIPLIER = 10000000

    @dispatch(int)
    @staticmethod
    def parse(x):  # flake8: noqa
        return x

    @dispatch(float)
    @staticmethod
    def parse(x):  # flake8: noqa
        return int(x * PriceParser.PRICE_MULTIPLIER)

    @dispatch(int)
    @staticmethod
    def display(x):  # flake8: noqa
        return round(x / PriceParser.PRICE_MULTIPLIER, 2)

    @dispatch(float)
    @staticmethod
    def display(x):  # flake8: noqa
        return round(x, 2)

    @dispatch(int, int)
    @staticmethod
    def display(x, dp):  # flake8: noqa
        return round(x / PriceParser.PRICE_MULTIPLIER, dp)

    @dispatch(float, int)
    @staticmethod
    def display(x, dp):  # flake8: noqa
        return round(x, dp)
