import pandas as pd

from qstrader.data.daily_bar_csv import CSVDailyBarDataSource


def test_convert_bar_frame_accepts_adjusted_close_column_name():
    data_source = CSVDailyBarDataSource.__new__(CSVDailyBarDataSource)
    data_source.adjust_prices = True

    bar_df = pd.DataFrame(
        {
            "Open": [100.0],
            "Close": [110.0],
            "Adjusted Close": [99.0],
        },
        index=pd.DatetimeIndex([pd.Timestamp("2024-01-02")]),
    )

    bid_ask_df = data_source._convert_bar_frame_into_bid_ask_df(bar_df)

    assert list(bid_ask_df["Bid"]) == [90.0, 99.0]
    assert list(bid_ask_df["Ask"]) == [90.0, 99.0]
