from __future__ import print_function

from abc import ABCMeta


class AbstractSentimentHandler(object):
    """
    AbstractSentimentHandler is an abstract base class providing
    an interface for all inherited sentiment analysis event handlers.

    Its goal is to allow subclassing for objects that read in file-based
    sentiment data (such as CSV files of date-asset-sentiment tuples), or
    streamed sentiment data from an API, and produce an event-driven output
    that sends SentimentEvent objects to the events queue.
    """

    __metaclass__ = ABCMeta

    def stream_next(self, stream_date=None):
        """
        Interface method for streaming the next SentimentEvent
        object to the events queue.
        """
        raise NotImplementedError("stream_next is not implemented in the base class!")
