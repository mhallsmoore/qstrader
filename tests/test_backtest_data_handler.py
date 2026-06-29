import pandas as pd

from qstrader.data.backtest_data_handler import BacktestDataHandler


class _LegacyDataSource:
    def __init__(self, prices):
        self.prices = prices

    def get_assets_historical_closes(self, start_dt, end_dt, asset_symbols):
        return self.prices.loc[start_dt:end_dt, asset_symbols]


class _AdjustedDataSource:
    def __init__(self, prices):
        self.prices = prices
        self.recorded_adjusted = None

    def get_assets_historical_closes(self, start_dt, end_dt, asset_symbols, adjusted=False):
        self.recorded_adjusted = adjusted
        return self.prices.loc[start_dt:end_dt, asset_symbols]


def test_historical_range_close_price_supports_legacy_data_sources():
    prices = pd.DataFrame(
        {"EQ:SPY": [100.0, 101.0]},
        index=pd.date_range("2024-01-01", periods=2, tz="UTC"),
    )
    data_handler = BacktestDataHandler(
        universe=["EQ:SPY"],
        data_sources=[_LegacyDataSource(prices)],
    )

    result = data_handler.get_assets_historical_range_close_price(
        prices.index[0], prices.index[-1], ["EQ:SPY"], adjusted=True
    )

    pd.testing.assert_frame_equal(result, prices)


def test_historical_range_close_price_forwards_adjusted_flag_when_supported():
    prices = pd.DataFrame(
        {"EQ:SPY": [100.0, 101.0]},
        index=pd.date_range("2024-01-01", periods=2, tz="UTC"),
    )
    data_source = _AdjustedDataSource(prices)
    data_handler = BacktestDataHandler(
        universe=["EQ:SPY"],
        data_sources=[data_source],
    )

    result = data_handler.get_assets_historical_range_close_price(
        prices.index[0], prices.index[-1], ["EQ:SPY"], adjusted=True
    )

    pd.testing.assert_frame_equal(result, prices)
    assert data_source.recorded_adjusted is True
