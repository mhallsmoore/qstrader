# The MIT License (MIT)
#
# Copyright (c) 2015 QuantStart.com, QuarkGluon Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os

import numpy as np
import pandas as pd
import pytz

from qstrader.exchange.price_volume_data_source import (
    PriceVolumeDataSource, PriceVolumeDataSourceException
)


class CSVBarDataPriceVolumeDataSource(PriceVolumeDataSource):
    """Derived class of PriceVolumeDataSource to handle
    OHLCV data obtained from a local CSV file.

    The CSV file is stored in a Pandas DataFrame for search
    efficiency purposes. Clients interact with the data by
    passing a timestamp into get_latest_asset_price_at_dt,
    which will return a tuple of bid and ask prices for a
    particular asset. 

    For OHLCV data the bid/ask is usually not present separately,
    but rather a midpoint is used. The tuple returns:
    (midpoint/midpoint)

    Parameters
    ----------
    asset : Asset
        The asset associated with the bar data.
    exchange_open_time_utc: pd.Timestamp, tz-aware
        The exchange opening time (needed for hours/minutes/seconds)
        in UTC timezone
    exchange_close_time_utc: pd.Timestamp, tz-aware
        The exchange closing time (needed for hours/minutes/seconds)
        in UTC timezone
    csv_dir : str
        The directory where the bar data is stored.
    filename : str, optional
        An optional filename to use for opening the CSV. If
        one is not provided then "****.csv" will be used where
        **** is the Asset symbol name.
    """

    def __init__(
        self, asset,
        exchange_open_time_utc,
        exchange_close_time_utc,
        csv_dir, filename=None
    ):
        """
        Initialise the CSVBarData class with an Asset, Exchange
        opening and closing times, CSV directory and an
        optional filename.
        """
        self.asset = asset
        self.exchange_open_time_utc = exchange_open_time_utc
        self.exchange_close_time_utc = exchange_close_time_utc
        self.csv_dir = csv_dir
        self.filename = filename
        self._set_correct_filename()
        self._open_csv_and_sort_on_datetimes()
        self._convert_ohlc_df_to_separate_open_closes()

    def _set_correct_filename(self):
        """
        Sets the correct filepath for the CSV file.
        """
        if self.filename is None:
            self.filename = "%s.csv" % self.asset.symbol
        self.csv_filepath = os.path.join(self.csv_dir, self.filename)

    def _open_csv_and_sort_on_datetimes(self):
        """
        Open the CSV file with Pandas and add to a DataFrame. Then sort
        it by the index column, which should be datetime-like.
        """
        # Check if the CSV file exists
        bar_error_msg = "Could not find CSV file '%s' on path '%s' while " \
            "attempting to load bar data CSV for asset '%s'." % (
                self.filename, self.csv_dir, self.asset.symbol
            )
        if not os.path.exists(self.csv_filepath):
            raise PriceVolumeDataSourceException(bar_error_msg)

        # Determine the date column name for use with indexing
        with open(self.csv_filepath, "r") as tmp_csv:
            header = tmp_csv.readline()
        header_split = header.strip().split(",")
        date_col_name = header_split[0]
        if date_col_name.lower() not in (
            "date", "datetime", "timestamp", "time"
        ):
            raise PriceVolumeDataSourceException(
                "Could not recognise date column with name '%s' "
                "in CSV file '%s' when attempting to open bar data "
                "CSV for asset '%s'." % (
                    date_col_name, self.filename, self.asset.symbol
                )
            )

        # Open the CSV file with Pandas
        try:
            self.csv_df = pd.read_csv(
                self.csv_filepath, parse_dates=["Date"]
            ).sort_values("Date", ascending=True)
        except FileNotFoundError:
            raise PriceVolumeDataSourceException(
                "Could not find CSV file '%s' on path '%s' while "
                "attempting to load bar data CSV for asset '%s'." % (
                    self.filename, self.csv_dir, self.asset.symbol
                )
            )

    def _convert_ohlc_df_to_separate_open_closes(self):
        """
        Converts the initial OHLCV DataFrame into a separate
        DataFrame, which stores separate timestamps for the open
        and closing prices.

        This enables the SimulatedExchange to assign more
        appropriate price values at market_open and
        market_close timestamps.
        """
        self.csv_df = self.csv_df.reindex(
            np.repeat(self.csv_df.index.values, 2), method='ffill'
        ) 
        self.csv_df.reset_index(inplace=True)
        self.csv_df.loc[0::2, "Date"] += pd.Timedelta(
            hours=self.exchange_open_time_utc.hour,
            minutes=self.exchange_open_time_utc.minute
        )
        self.csv_df.loc[1::2, "Date"] += pd.Timedelta(
            hours=self.exchange_close_time_utc.hour,
            minutes=self.exchange_close_time_utc.minute
        )
        self.csv_df.loc[0::2, "Price"] = self.csv_df.loc[0::2, "Open"]
        self.csv_df.loc[1::2, "Price"] = self.csv_df.loc[1::2, "Close"]

        dti = pd.DatetimeIndex(self.csv_df["Date"]).tz_localize("UTC")
        self.csv_df = self.csv_df.set_index(dti)
        self.csv_df.drop(
            [
                "Open", "High", "Low", "Close",
                "Adj Close", "index"
            ],
            axis=1, inplace=True
        )

    def get_latest_asset_price_at_dt(self, dt):
        """
        Return a tuple of the bid/ask information
        for the asset, making use of the last available price
        in the past before or equal to the timestamp 'dt'.

        Since the majority of OHLCV data utilises midpoint
        pricing the tuple will return (midpoint, midpoint).

        Parameters
        ----------
        dt : pd.Timestamp
            The datetime to obtain the current price for.
        """
        try:
            row = self.csv_df.ix[
                self.csv_df.index.get_loc(dt, method='pad')
            ]
        except KeyError:  # Before start date
            return (np.NaN, np.NaN)
        else:
            return (row.Price, row.Price)
