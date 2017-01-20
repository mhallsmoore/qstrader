import os

import pandas as pd

from .base import AbstractSentimentHandler
from ..event import SentimentEvent


class SentdexSentimentHandler(AbstractSentimentHandler):
    """
    SentdexSentimentHandler is designed to provide a backtesting
    sentiment analysis handler for the Sentdex sentiment analysis
    provider (http://sentdex.com/financial-analysis/).

    It uses a CSV file with date-ticker-sentiment tuples/rows.
    Hence in order to avoid implicit lookahead bias a specific
    method is provided "stream_sentiment_events_on_date" that only
    allows sentiment signals to be retrieved for a particular date.
    """
    def __init__(
        self, csv_dir, filename,
        events_queue, tickers=None,
        start_date=None, end_date=None
    ):
        self.csv_dir = csv_dir
        self.filename = filename
        self.events_queue = events_queue
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.sent_df = self._open_sentiment_csv()

    def _open_sentiment_csv(self):
        """
        Opens the CSV file containing the sentiment analysis
        information for all represented stocks and places
        it into a pandas DataFrame.
        """
        sentiment_path = os.path.join(self.csv_dir, self.filename)
        sent_df = pd.read_csv(
            sentiment_path, parse_dates=True,
            header=0, index_col=0,
            names=("Date", "Ticker", "Sentiment")
        )
        if self.start_date is not None:
            sent_df = sent_df[self.start_date.strftime("%Y-%m-%d"):]
        if self.end_date is not None:
            sent_df = sent_df[:self.end_date.strftime("%Y-%m-%d")]
        if self.tickers is not None:
            sent_df = sent_df[sent_df["Ticker"].isin(self.tickers)]
        return sent_df

    def stream_next(self, stream_date=None):
        """
        Stream the next set of ticker sentiment values into
        SentimentEvent objects.
        """
        if stream_date is not None:
            stream_date_str = stream_date.strftime("%Y-%m-%d")
            date_df = self.sent_df.ix[stream_date_str:stream_date_str]
            for row in date_df.iterrows():
                sev = SentimentEvent(
                    stream_date, row[1]["Ticker"],
                    row[1]["Sentiment"]
                )
                self.events_queue.put(sev)
        else:
            print("No stream_date provided for stream_next sentiment event!")
