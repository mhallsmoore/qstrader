from __future__ import print_function

import os

import pandas as pd

from .base import AbstractTickPriceHandler
from ..event import TickEvent
from ..price_parser import PriceParser


class HistoricCSVTickPriceHandler(AbstractTickPriceHandler):
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
                    "bid": PriceParser.parse(row0["Bid"]),
                    "ask": PriceParser.parse(row0["Ask"]),
                    "timestamp": dft.index[0]
                }
                self.tickers[ticker] = ticker_prices
            except OSError:
                print(
                    "Could not subscribe ticker %s "
                    "as no data CSV found for pricing." % ticker
                )
        else:
            print(
                "Could not subscribe ticker %s "
                "as is already subscribed." % ticker
            )

    def _create_event(self, index, ticker, row):
        """
        Obtain all elements of the bar a row of dataframe
        and return a TickEvent
        """
        bid = PriceParser.parse(row["Bid"])
        ask = PriceParser.parse(row["Ask"])
        tev = TickEvent(ticker, index, bid, ask)
        return tev

    def stream_next(self):
        """
        Place the next TickEvent onto the event queue.
        """
        try:
            index, row = next(self.tick_stream)
        except StopIteration:
            self.continue_backtest = False
            return
        ticker = row["Ticker"]
        tev = self._create_event(index, ticker, row)
        self._store_event(tev)
        self.events_queue.put(tev)
