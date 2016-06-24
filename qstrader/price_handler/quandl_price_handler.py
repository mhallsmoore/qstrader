import datetime
from decimal import Decimal, getcontext, ROUND_HALF_DOWN
import os, os.path

import pandas as pd

from qstrader.event.event import BarEvent
from qstrader.price_handler.price_handler import PriceHandler
from qstrader.settings import DEFAULT as settings

import quandl

class QuandlPriceHandler(PriceHandler):
    """
    QuandlBarPriceHandler is designed to read CSV files of
    Quandl daily Open-High-Low-Close-Volume (OHLCV) data
    for each requested financial instrument and stream those to
    the provided events queue as BarEvents.

    Note: quandl.get() already retrieves data in Pandas DataFrames.  So instead
          of storing those as CSV files, just use the the DataFrame directly.
          Later, cache the data as a CSV or sqlite db for better
          performance.
    """
    def __init__(self, csv_dir, events_queue, init_tickers=None,
                 config=settings):
        """
        Takes the CSV directory, the events queue and a possible
        list of initial ticker (quandl) symbols then creates an (optional)
        list of ticker subscriptions and associated prices.
        """
        # Globally set the Quandl Key and other quandl config parms
        # (see comment in quandl_conf.py)
        #
        # Note:
        # quandl.get() also supports a parm called api_key.  Specifying the
        # api_key and setting the key directly in the ApiConfig class
        # effectively are the same thing.  The key only needs to be specified
        # here once, as opposed to on each API call.
        quandl.ApiConfig.api_key = config.QUANDL_API_KEY
        quandl.ApiConfig.api_base = config.QUANDL_API_BASE
        quandl.ApiConfig.api_version = config.QUANDL_API_VERSION
        quandl.ApiConfig.page_limit = config.QUANDL_PAGE_LIMIT


        self.type = "BAR_HANDLER"
        self.csv_dir = csv_dir
        self.events_queue = events_queue
        self.continue_backtest = True
        self.tickers = {}
        self.tickers_data = {}
        if init_tickers is not None:
            for ticker in init_tickers:
                self.subscribe_ticker(ticker)
        self.bar_stream = self._merge_sort_ticker_data()

    def _open_ticker_price_csv(self, ticker):
        """
        Opens the CSV files containing the equities ticks from
        the specified CSV data directory, converting them into
        them into a pandas DataFrame, stored in a dictionary.
        """
        # TBD: for now just get straight from quandl
        # TBD: Input start_date from user.  For now just hard code it.
        self.tickers_data[ticker] = quandl.get(ticker,
                                               start_date="2016-05-01")
        self.tickers_data[ticker]["Ticker"] = ticker
        """
        ticker_path = os.path.join(self.csv_dir, "%s.csv" % ticker)
        self.tickers_data[ticker] = pd.io.parsers.read_csv(
            ticker_path, header=0, parse_dates=True,
            index_col=0, names=(
                "Date", "Open", "High", "Low",
                "Last", "Change", "Settle", "Volume"
            )
        )
        self.tickers_data[ticker]["Ticker"] = ticker
        """

    def _merge_sort_ticker_data(self):
        """
        Concatenates all of the separate equities DataFrames
        into a single DataFrame that is time ordered, allowing tick
        data events to be added to the queue in a chronological fashion.

        Note that this is an idealised situation, utilised solely for
        backtesting. In live trading ticks may arrive "out of order".
        """
        return pd.concat(
            self.tickers_data.values()
        ).sort_index().iterrows()

    def subscribe_ticker(self, ticker):
        """
        Subscribes the price handler to a new ticker symbol.
        """
        if ticker not in self.tickers:
            try:
                self._open_ticker_price_csv(ticker)
                dft = self.tickers_data[ticker]
                row0 = dft.iloc[0]
                ticker_prices = {
                    "last": Decimal(
                        str(row0["Last"])
                    ).quantize(Decimal("0.00001")),
                    "settle": Decimal(
                        str(row0["Settle"])
                    ).quantize(Decimal("0.00001")),
                    "timestamp": dft.index[0]
                }
                self.tickers[ticker] = ticker_prices
            except OSError:
                print(
                    "Could not subscribe ticker %s " \
                    "as no data CSV found for pricing." % ticker
                )
        else:
            print(
                "Could not subscribe ticker %s " \
                "as is already subscribed." % ticker
            )

    def get_last_close(self, ticker):
        """
        Returns the most recent actual (unadjusted) closing price.
        """
        if ticker in self.tickers:
            close_price = self.tickers[ticker]["last"]
            return close_price
        else:
            print(
                "Close price for ticker %s is not " \
                "available from the QuandlPriceHandler."
            )
            return None

    def stream_next_bar(self):
        """
        Place the next BarEvent onto the event queue.
        """
        try:
            index, row = next(self.bar_stream)
        except StopIteration:
            self.continue_backtest = False
            return

        # Obtain all elements of the bar from the dataframe
        getcontext().rounding = ROUND_HALF_DOWN
        ticker = row["Ticker"]
        open_price = Decimal(str(row["Open"])).quantize(Decimal("0.00001"))
        high_price = Decimal(str(row["High"])).quantize(Decimal("0.00001"))
        low_price = Decimal(str(row["Low"])).quantize(Decimal("0.00001"))
        last_price = Decimal(str(row["Last"])).quantize(Decimal("0.00001"))
        settle_price = Decimal(str(row["Settle"])).quantize(Decimal("0.00001"))
        volume = int(row["Volume"])

        # Create decimalised prices for
        # closing price and adjusted closing price
        self.tickers[ticker]["last"] = last_price
        self.tickers[ticker]["settle"] = settle_price
        self.tickers[ticker]["timestamp"] = index

        # Create the tick event for the queue
        period = 86400  # Seconds in a day
        bev = BarEvent(
            ticker, index, period, open_price,
            high_price, low_price, last_price,
            volume, settle_price
        )
        self.events_queue.put(bev)
