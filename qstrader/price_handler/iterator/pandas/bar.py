from ..base import AbstractBarEventIterator


class PandasDataFrameBarEventIterator(AbstractBarEventIterator):
    """
    PandasDataFrameBarEventIterator is designed to read a Pandas DataFrame like

                      Open        High         Low       Close    Volume   Adj Close
    Date
    2010-01-04  626.951088  629.511067  624.241073  626.751061   3927000  313.062468
    2010-01-05  627.181073  627.841071  621.541045  623.991055   6031900  311.683844
    2010-01-06  625.861078  625.861078  606.361042  608.261023   7987100  303.826685
    2010-01-07  609.401025  610.001045  592.651008  594.101005  12876600  296.753749
    ...                ...         ...         ...         ...       ...         ...
    2016-07-18  722.710022  736.130005  721.190002  733.780029   1283300  733.780029
    2016-07-19  729.890015  736.989990  729.000000  736.960022   1222600  736.960022
    2016-07-20  737.330017  742.130005  737.099976  741.190002   1278100  741.190002
    2016-07-21  740.359985  741.690002  735.830994  738.630005    969100  738.630005

    [1649 rows x 6 columns]

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
        self.tickers_lst = [ticker]
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
