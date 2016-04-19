from __future__ import print_function
from abc import ABCMeta, abstractmethod
import datetime
from decimal import Decimal, getcontext, ROUND_HALF_DOWN
import os, os.path

import pandas as pd

from qstrader.event.event import TickEvent


class PriceHandler(object):
    """
    PriceHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) PriceHandler object is to output a set of
    bid/ask/timestamp "ticks" for each financial instrument and place 
    them into an event queue.

    This will replicate how a live strategy would function as current
    tick data would be streamed via a brokerage. Thus a historic and live
    system will be treated identically by the rest of the QSTrader suite.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def subscribe_ticker(self, ticker):
        """
        Subscribes the price handler to a new ticker symbol.
        """
        raise NotImplementedError("Should implement subscribe_ticker()")

    @abstractmethod
    def unsubscribe_ticker(self, ticker):
        """
        Unsubscribes the price handler from a current ticker symbol.
        """
        raise NotImplementedError("Should implement unsubscribe_ticker()")

    @abstractmethod
    def get_best_bid_ask(self, ticker):
        """
        Returns the most recent bid/ask price for a ticker.
        """
        raise NotImplementedError("Should implement get_best_bid_ask()")

    @abstractmethod
    def stream_next_tick(self):
        """
        Place the next TickEvent onto the event queue.
        """
        raise NotImplementedError("Should implement stream_next_tick()")


class HistoricCSVPriceHandler(PriceHandler):
    """
    HistoricCSVPriceHandler is designed to read CSV files of
    tick data for each requested financial instrument and 
    stream those to the provided events queue as TickEvents.
    """
    def __init__(self, csv_dir, events_queue, init_tickers=None):
        """
        Takes the CSV directory, the events queue and a possible
        list of initial ticker symbols, then creates an (optional)
        list of ticker subscriptions and associated prices.
        """
        self.csv_dir = csv_dir
        self.events_queue = events_queue
        self.continue_backtest = True
        self.tickers = {}
        self.tickers_data = {}
        if init_tickers is not None:
            for ticker in init_tickers:
                self.subscribe_ticker(ticker)
        self.tick_stream = self._merge_sort_ticker_data()

    def _open_ticker_price_csv(self, ticker):
        """
        Opens the CSV files containing the equities ticks from
        the specified CSV data directory, converting them into
        them into a pandas DataFrame, stored in a dictionary.
        """
        ticker_path = os.path.join(self.csv_dir, "%s.csv" % ticker)
        self.tickers_data[ticker] = pd.io.parsers.read_csv(
            ticker_path, header=0, parse_dates=True, 
            dayfirst=True, index_col=1,
            names=("Ticker", "Time", "Bid", "Ask")
        )

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
                    "bid": Decimal(str(row0["Bid"])), 
                    "ask": Decimal(str(row0["Ask"])), 
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

    def unsubscribe_ticker(self, ticker):
        """
        Unsubscribes the price handler from a current ticker symbol.
        """
        try:
            self.tickers.pop(ticker, None)
            self.tickers_data.pop(ticker, None)
        except KeyError:
            print(
                "Could not unsubscribe ticker %s " \
                "as it was never subscribed." % ticker
            )

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
                "Bid/ask values for ticker %s are not " \
                "available from the PriceHandler."
            )
            return None, None

    def stream_next_tick(self):
        """
        Place the next TickEvent onto the event queue.
        """
        try:
            index, row = next(self.tick_stream)
        except StopIteration:
            self.continue_backtest = False
            return
        
        getcontext().rounding = ROUND_HALF_DOWN
        ticker = row["Ticker"]
        bid = Decimal(str(row["Bid"])).quantize(
            Decimal("0.00001")
        )
        ask = Decimal(str(row["Ask"])).quantize(
            Decimal("0.00001")
        )

        # Create decimalised prices for traded pair
        self.tickers[ticker]["bid"] = bid
        self.tickers[ticker]["ask"] = ask
        self.tickers[ticker]["timestamp"] = index

        # Create the tick event for the queue
        tev = TickEvent(ticker, index, bid, ask)
        self.events_queue.put(tev)


class YahooDailyBarPriceHandler(PriceHandler):
    """
    YahooDailyBarPriceHandler is designed to read CSV files of
    Yahoo Finance daily Open-High-Low-Close-Volum (OHLCV) data
    for each requested financial instrument and stream those to 
    the provided events queue as TickEvents, with bid/ask spread
    set to 0 (i.e. bid and ask are the same).
    """
    def __init__(self, csv_dir, events_queue, init_tickers=None):
        """
        Takes the CSV directory, the events queue and a possible
        list of initial ticker symbols, then creates an (optional)
        list of ticker subscriptions and associated prices.
        """
        self.csv_dir = csv_dir
        self.events_queue = events_queue
        self.continue_backtest = True
        self.tickers = {}
        self.tickers_data = {}
        if init_tickers is not None:
            for ticker in init_tickers:
                self.subscribe_ticker(ticker)
        self.tick_stream = self._merge_sort_ticker_data()

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
                adj_close = row0["Adj Close"]
                ticker_prices = {
                    "bid": Decimal(str(adj_close)), 
                    "ask": Decimal(str(adj_close)), 
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

    def unsubscribe_ticker(self, ticker):
        """
        Unsubscribes the price handler from a current ticker symbol.
        """
        try:
            self.tickers.pop(ticker, None)
            self.tickers_data.pop(ticker, None)
        except KeyError:
            print(
                "Could not unsubscribe ticker %s " \
                "as it was never subscribed." % ticker
            )

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
                "Bid/ask values for ticker %s are not " \
                "available from the PriceHandler."
            )
            return None, None

    def stream_next_tick(self):
        """
        Place the next TickEvent onto the event queue.
        """
        try:
            index, row = next(self.tick_stream)
        except StopIteration:
            self.continue_backtest = False
            return
        
        getcontext().rounding = ROUND_HALF_DOWN
        ticker = row["Ticker"]
        adj_close = row["Adj Close"]
        bid = Decimal(str(adj_close)).quantize(
            Decimal("0.00001")
        )
        ask = Decimal(str(adj_close)).quantize(
            Decimal("0.00001")
        )

        # Create decimalised prices for traded pair
        self.tickers[ticker]["bid"] = bid
        self.tickers[ticker]["ask"] = ask
        self.tickers[ticker]["timestamp"] = index

        # Create the tick event for the queue
        tev = TickEvent(ticker, index, bid, ask)
        self.events_queue.put(tev)