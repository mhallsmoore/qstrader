from __future__ import print_function

from abc import ABCMeta


class AbstractPriceHandler(object):
    """
    PriceHandler is a base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) PriceHandler object is to output a set of
    TickEvents or BarEvents for each financial instrument and place
    them into an event queue.

    This will replicate how a live strategy would function as current
    tick/bar data would be streamed via a brokerage. Thus a historic and live
    system will be treated identically by the rest of the QSTrader suite.
    """

    __metaclass__ = ABCMeta

    def unsubscribe_ticker(self, ticker):
        """
        Unsubscribes the price handler from a current ticker symbol.
        """
        try:
            self.tickers.pop(ticker, None)
            self.tickers_data.pop(ticker, None)
        except KeyError:
            print(
                "Could not unsubscribe ticker %s "
                "as it was never subscribed." % ticker
            )


class AbstractTickPriceHandler(AbstractPriceHandler):
    def istick(self):
        return True

    def isbar(self):
        return False


class AbstractBarPriceHandler(AbstractPriceHandler):
    def istick(self):
        return False

    def isbar(self):
        return True
