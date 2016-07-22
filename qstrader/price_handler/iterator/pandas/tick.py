from ..base import AbstractTickEventIterator


class PandasDataFrameTickEventIterator(AbstractTickEventIterator):
    """
    PandasPanelBarEventIterator is designed to read a Pandas DataFrame like

                                   Bid        Ask
    Time
    2016-02-01 00:00:01.358  683.56000  683.58000
    2016-02-01 00:00:02.544  683.55998  683.58002
    2016-02-01 00:00:03.765  683.55999  683.58001
    ...
    2016-02-01 00:00:10.823  683.56001  683.57999
    2016-02-01 00:00:12.221  683.56000  683.58000
    2016-02-01 00:00:13.546  683.56000  683.58000

    with tick data (bid/ask)
    for one financial instrument and iterate TickEvents.
    """
    def __init__(self, df, ticker):
        """
        Takes the the events queue, ticker and Pandas DataFrame
        """
        self.data = df
        self.ticker = ticker
        self.tickers_lst = [ticker]
        self._itr_bar = self.data.iterrows()

    def __next__(self):
        index, row = next(self._itr_bar)
        price_event = self._create_event(index, self.ticker, row)
        return price_event


class PandasPanelTickEventIterator(AbstractTickEventIterator):
    """
    PandasPanelBarEventIterator is designed to read a Pandas Panel like

    <class 'pandas.core.panel.Panel'>
    Dimensions: 2 (items) x 20 (major_axis) x 2 (minor_axis)
    Items axis: Bid to Ask
    Major_axis axis: 2016-02-01 00:00:01.358000 to 2016-02-01 00:00:14.153000
    Minor_axis axis: GOOG to MSFT

    with tick data (bid/ask)
    for several financial instruments and iterate TickEvents.
    """
    def __init__(self, panel):
        self.data = panel
        self._itr_ticker_bar = self.data.transpose(1, 0, 2).iteritems()
        self.tickers_lst = self.data.minor_axis
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
        bev = self._create_event(self.index, ticker, row)
        return bev


def PandasTickEventIterator(data, ticker=None):
    """
    PandasTickEventIterator returns a price iterator designed to read
    a Pandas DataFrame (or a Pandas Panel) with tick data (bid/ask)
    for one (or several) financial instrument and iterate TickEvents.
    """
    if hasattr(data, 'minor_axis'):
        return PandasPanelTickEventIterator(data)
    else:
        return PandasDataFrameTickEventIterator(data, ticker)
