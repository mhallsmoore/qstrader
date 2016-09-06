from ...price_parser import PriceParser
from ...event import BarEvent, TickEvent
from ...exception import EmptyTickEvent, EmptyBarEvent


class AbstractPriceEventIterator(object):
    def __iter__(self):
        return self

    def next(self):
        return self.__next__()


class AbstractBarEventIterator(AbstractPriceEventIterator):
    def _create_event(self, index, period, ticker, row):
        """
        Obtain all elements of the bar from a row of dataframe
        and return a BarEvent
        """
        try:
            open_price = PriceParser.parse(row["Open"])
            high_price = PriceParser.parse(row["High"])
            low_price = PriceParser.parse(row["Low"])
            close_price = PriceParser.parse(row["Close"])
            adj_close_price = PriceParser.parse(row["Adj Close"])
            volume = int(row["Volume"])

            # Create the tick event for the queue
            bev = BarEvent(
                ticker, index, period, open_price,
                high_price, low_price, close_price,
                volume, adj_close_price
            )
            return bev
        except ValueError:
            raise EmptyBarEvent("row %s %s %s %s can't be convert to BarEvent" % (index, period, ticker, row))


class AbstractTickEventIterator(AbstractPriceEventIterator):
    def _create_event(self, index, ticker, row):
        """
        Obtain all elements of the bar a row of dataframe
        and return a TickEvent
        """
        try:
            bid = PriceParser.parse(row["Bid"])
            ask = PriceParser.parse(row["Ask"])
            tev = TickEvent(ticker, index, bid, ask)
            return tev
        except ValueError:
            raise EmptyTickEvent("row %s %s %s can't be convert to TickEvent" % (index, ticker, row))
