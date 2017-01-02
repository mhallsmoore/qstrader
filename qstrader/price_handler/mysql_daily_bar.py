import os

import pandas as pd
import MySQLdb as mdb

from ..price_parser import PriceParser
from .base import AbstractBarPriceHandler
from ..event import BarEvent

class MySQLDailyCsvBarPriceHandler(AbstractBarPriceHandler):
    
    def __init__(
        self, events_queue,
        db_user, db_pass,
        db_host="localhost",
        db_name="securities_master",
        init_tickers=None,
        start_date=None, end_date=None
    ):

        self.events_queue = events_queue        
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_host = db_host
        self.db_name = db_name
        self.continue_backtest = True
        self.tickers = {}
        self.tickers_data = {}
        if init_tickers is not None:
            for ticker in init_tickers:
                self.subscribe_ticker(ticker)
        self.start_date = start_date
        self.end_date = end_date
        self.bar_stream = self._merge_sort_ticker_data()        

    def _open_ticker_price(self, ticker):
        """
        Opens the CSV files containing the equities ticks from
        the specified CSV data directory, converting them into
        them into a pandas DataFrame, stored in a dictionary.
        """
        
        sql = """SELECT	daily_price.price_date,
                        daily_price.open_price,
                        daily_price.high_price,
                        daily_price.low_price,
                        daily_price.close_price,
                        daily_price.volume,
                        daily_price.adj_close_price
                FROM {0}.daily_price
                INNER JOIN {1}.symbol
                ON daily_price.symbol_id=symbol.id
                WHERE symbol.ticker='{2}'""".format(self.db_name,
                                                   self.db_name,
                                                   ticker)
        
        con = "mysql://{0}:{1}@{2}/{3}".format(self.db_user,
                                               self.db_pass,
                                               self.db_host,
                                               self.db_name)
        
        self.tickers_data[ticker] = pd.read_sql_query(sql, con,
                                                      index_col="price_date")
        
        self.tickers_data[ticker].columns = [
                "Date", "Open", "High", "Low",
                "Close", "Volume", "Adj Close"
            ]
        
        self.tickers_data[ticker]["Ticker"] = ticker

    def _merge_sort_ticker_data(self):
        """
        Concatenates all of the separate equities DataFrames
        into a single DataFrame that is time ordered, allowing tick
        data events to be added to the queue in a chronological fashion.

        Note that this is an idealised situation, utilised solely for
        backtesting. In live trading ticks may arrive "out of order".
        """
        df = pd.concat(self.tickers_data.values()).sort_index()
        start = None
        end = None
        if self.start_date is not None:
            start = df.index.searchsorted(self.start_date)
        if self.end_date is not None:
            end = df.index.searchsorted(self.end_date)
        # Determine how to slice
        if start is None and end is None:
            return df.iterrows()
        elif start is not None and end is None:
            return df.ix[start:].iterrows()
        elif start is None and end is not None:
            return df.ix[:end].iterrows()
        else:
            return df.ix[start:end].iterrows()

    def subscribe_ticker(self, ticker):
        """
        Subscribes the price handler to a new ticker symbol.
        """
        if ticker not in self.tickers:
            self._open_ticker_price(ticker)
            dft = self.tickers_data[ticker]
            row0 = dft.iloc[0]

            close = PriceParser.parse(row0["Close"])
            adj_close = PriceParser.parse(row0["Adj Close"])

            ticker_prices = {
                "close": close,
                "adj_close": adj_close,
                "timestamp": dft.index[0]
            }
            self.tickers[ticker] = ticker_prices
        else:
            print(
                "Could not subscribe ticker %s "
                "as is already subscribed." % ticker
            )
            
    def _create_event(self, index, period, ticker, row):
        """
        Obtain all elements of the bar from a row of dataframe
        and return a BarEvent
        """
        open_price = PriceParser.parse(row["Open"])
        high_price = PriceParser.parse(row["High"])
        low_price = PriceParser.parse(row["Low"])
        close_price = PriceParser.parse(row["Close"])
        adj_close_price = PriceParser.parse(row["Adj Close"])
        volume = int(row["Volume"])
        bev = BarEvent(
            ticker, index, period, open_price,
            high_price, low_price, close_price,
            volume, adj_close_price
        )
        return bev

    def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """
        try:
            index, row = next(self.bar_stream)
        except StopIteration:
            self.continue_backtest = False
            return
        # Obtain all elements of the bar from the dataframe
        ticker = row["Ticker"]
        period = 86400  # Seconds in a day
        # Create the tick event for the queue
        bev = self._create_event(index, period, ticker, row)
        # Store event
        self._store_event(bev)
        # Send event to queue
        self.events_queue.put(bev)