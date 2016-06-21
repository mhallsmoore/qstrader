import datetime
from decimal import Decimal, getcontext, ROUND_HALF_DOWN
import os, os.path

import pandas as pd

from qstrader.event.event import BarEvent
from qstrader.price_handler.price_handler import PriceHandler

try:
    from qstrader import settings
except ImportError:
    print(
        "Could not import settings.py. Have you copied " \
        "settings.py.example to settings.py and configured " \
        "your QSTrader settings?"
    )

class YahooDailyBarPriceHandler(PriceHandler):
    """
    YahooDailyBarPriceHandler is designed to read CSV files of
    Yahoo Finance daily Open-High-Low-Close-Volume (OHLCV) data
    for each requested financial instrument and stream those to
    the provided events queue as BarEvents.
    """
    def __init__(self, csv_dir, events_queue, init_tickers=None):
        """
        Takes the CSV directory, the events queue and a possible
        list of initial ticker symbols then creates an (optional)
        list of ticker subscriptions and associated prices.
        """
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
        ticker_path = os.path.join(self.csv_dir, "%s.csv" % ticker)
        self.tickers_data[ticker] = pd.io.parsers.read_csv(
            ticker_path, header=0, parse_dates=True,
            index_col=0, names=(
                "Date", "Open", "High", "Low",
                "Close", "Volume", "Adj Close"
            )
        )
        self.tickers_data[ticker]["Ticker"] = ticker

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

                close =  int(Decimal(str(row0["Close"])).quantize(Decimal("0.0001")) * settings.PRICE_MULTIPLIER)
                adj_close = int(Decimal( str(row0["Adj Close"]) ).quantize(Decimal("0.0001")) * settings.PRICE_MULTIPLIER)

                ticker_prices = {
                    "close": close,
                    "adj_close": adj_close,
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
            close_price = self.tickers[ticker]["close"]
            return close_price
        else:
            print(
                "Close price for ticker %s is not " \
                "available from the YahooDailyBarPriceHandler."
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
        open_price = int(row["Open"] * 100) * settings.PRICE_MULTIPLIER // 100
        high_price = int(row["High"] * 100) * settings.PRICE_MULTIPLIER // 100
        low_price = int(row["Low"] * 100) * settings.PRICE_MULTIPLIER // 100
        close_price = int(row["Close"] * 100) * settings.PRICE_MULTIPLIER // 100
        adj_close_price = int(row["Adj Close"] * 100) * settings.PRICE_MULTIPLIER // 100
        volume = int(row["Volume"])

        # Create decimalised prices for
        # closing price and adjusted closing price
        self.tickers[ticker]["close"] = close_price
        self.tickers[ticker]["adj_close"] = adj_close_price
        self.tickers[ticker]["timestamp"] = index

        # Create the tick event for the queue
        period = 86400  # Seconds in a day
        bev = BarEvent(
            ticker, index, period, open_price,
            high_price, low_price, close_price,
            volume, adj_close_price
        )
        self.events_queue.put(bev)
