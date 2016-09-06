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

    def get_last_timestamp(self, ticker):
        """
        Returns the most recent actual timestamp for a given ticker
        """
        if ticker in self.tickers:
            timestamp = self.tickers[ticker]["timestamp"]
            return timestamp
        else:
            print(
                "Timestamp for ticker %s is not "
                "available from the %s." % (ticker, self.__class__.__name__)
            )
            return None


class AbstractTickPriceHandler(AbstractPriceHandler):
    def istick(self):
        return True

    def isbar(self):
        return False

    def _store_event(self, event):
        """
        Store price event for bid/ask
        """
        ticker = event.ticker
        self.tickers[ticker]["bid"] = event.bid
        self.tickers[ticker]["ask"] = event.ask
        self.tickers[ticker]["timestamp"] = event.time

    def get_best_bid_ask(self, ticker):
        """
        Returns the most recent bid/ask price for a ticker.
        """
        if ticker in self.tickers:
            bid = self.tickers[ticker]["bid"]
            ask = self.tickers[ticker]["ask"]
            return bid, ask
        else:
            print(
                "Bid/ask values for ticker %s are not "
                "available from the PriceHandler." % ticker
            )
            return None, None


class AbstractBarPriceHandler(AbstractPriceHandler):
    def istick(self):
        return False

    def isbar(self):
        return True

    def _store_event(self, event):
        """
        Store price event for closing price and adjusted closing price
        """
        ticker = event.ticker
        self.tickers[ticker]["close"] = event.close_price
        self.tickers[ticker]["adj_close"] = event.adj_close_price
        self.tickers[ticker]["timestamp"] = event.time

    def get_last_close(self, ticker):
        """
        Returns the most recent actual (unadjusted) closing price.
        """
        if ticker in self.tickers:
            close_price = self.tickers[ticker]["close"]
            return close_price
        else:
            print(
                "Close price for ticker %s is not "
                "available from the YahooDailyBarPriceHandler."
            )
            return None
