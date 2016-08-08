from .base import AbstractPriceHandler, AbstractBarPriceHandler, AbstractTickPriceHandler
from .iterator.base import AbstractBarEventIterator, AbstractTickEventIterator
from ..exception import EmptyTickEvent, EmptyBarEvent


class AbstractGenericHandler(AbstractPriceHandler):
    def __init__(self, events_queue, price_event_iterator):
        self.events_queue = events_queue
        self.price_event_iterator = price_event_iterator
        self.continue_backtest = True
        self.tickers = {}
        for ticker in self.tickers_lst:
            self.tickers[ticker] = {}

    def stream_next(self):
        """
        Place the next PriceEvent (BarEvent or TickEvent) onto the event queue.
        """
        try:
            price_event = next(self.price_event_iterator)
        except StopIteration:
            self.continue_backtest = False
            return
        except (EmptyTickEvent, EmptyBarEvent):
            return
        self._store_event(price_event)
        self.events_queue.put(price_event)

    @property
    def tickers_lst(self):
        return self.price_event_iterator.tickers_lst


class GenericBarHandler(AbstractGenericHandler, AbstractBarPriceHandler):
    pass


class GenericTickHandler(AbstractGenericHandler, AbstractTickPriceHandler):
    pass


def GenericPriceHandler(events_queue, price_event_iterator):
    if isinstance(price_event_iterator, AbstractBarEventIterator):
        return GenericBarHandler(events_queue, price_event_iterator)
    elif isinstance(price_event_iterator, AbstractTickEventIterator):
        return GenericTickHandler(events_queue, price_event_iterator)
    else:
        raise NotImplementedError("price_event_iterator must be instance of")
