from ..base import AbstractBarEventIterator


class IBBarEventIterator(AbstractBarEventIterator)
class PandasDataFrameBarEventIterator(AbstractBarEventIterator):
    """
    with Open-High-Low-Close-Volume (OHLCV) data (bar)
    for one financial instrument and iterate BarEvents.
    """
    def __init__(self, df, period, ticker):
        """
        Takes the the events queue, ticker and Pandas DataFrame
        """
        self.data = df
        self.period = period
        self.ticker = ticker
        self.tickers_list = [ticker]
        self._itr_bar = self.data.iterrows()

    def __next__(self):
        index, row = next(self._itr_bar)
        price_event = self._create_event(index, self.period, self.ticker, row)
        return price_event


class PandasPanelBarEventIterator(AbstractBarEventIterator):
    """
    PandasPanelBarEventIterator is designed to read a Pandas Panel like

    <class 'pandas.core.panel.Panel'>
    Dimensions: 6 (items) x 1649 (major_axis) x 2 (minor_axis)
    Items axis: Open to Adj Close
    Major_axis axis: 2010-01-04 00:00:00 to 2016-07-21 00:00:00
    Minor_axis axis: GOOG to IBM

    with Open-High-Low-Close-Volume (OHLCV) data (bar)
    for several financial instruments and iterate BarEvents.
    """
    def __init__(self, panel, period):
        self.data = panel
        self.period = period
        self._itr_ticker_bar = self.data.transpose(1, 0, 2).iteritems()
        self.tickers_list = self.data.minor_axis
        self._next_ticker_bar()

    def _next_ticker_bar(self):
        self.index, self.df = next(self._itr_ticker_bar)
        self._itr_bar = self.df.iteritems()

    def __next__(self):
        try:
            ticker, row = next(self._itr_bar)
        except StopIteration:
            self._next_ticker_bar()
            ticker, row = next(self._itr_bar)
        price_event = self._create_event(self.index, self.period, ticker, row)
        return price_event


def PandasBarEventIterator(data, period, ticker=None):
    """
    PandasBarEventIterator returns a price iterator designed to read
    a Pandas DataFrame (or a Pandas Panel)
    with Open-High-Low-Close-Volume (OHLCV) data (bar)
    for one (or several) financial instrument and iterate BarEvents.
    """
    if hasattr(data, 'minor_axis'):
        return PandasPanelBarEventIterator(data, period)
    else:
        return PandasDataFrameBarEventIterator(data, period, ticker)
