from multipledispatch import dispatch
from qstrader import settings

class PriceParser(object):
    """
    PriceParser will abstract away the underlying number type (Float or Integer)
    using multiple dispatch. The allows the rest of the system to use
    whatever underlying number type suits the user best (accuracy, speed
    and comfort with complexity).

    This only parses numbers into preferred types, and provides a nice display.
    Means you can use all normal operators normally with numbers once they
    have been parsed.

    All DISPLAY code should run through the display() method.

    ALL NUMBERS that enter the system from an external source should run through
    the parse() method.

    TODO support Decimal?
    TODO more explanation. Maybe Docs even.

    TODO PARSE PRICE -- volume is always int, price should be the x10,000,000
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
        return x * PriceParser.PRICE_MULTIPLIER

    # Display
    @staticmethod
    @dispatch(int)
    def display_price(x):
        return str(x / PriceParser.PRICE_MULTIPLIER)

    @staticmethod
    @dispatch(float)
    def display_price(x):
        return str(x)
