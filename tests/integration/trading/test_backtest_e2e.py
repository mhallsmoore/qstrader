import os

import pandas as pd
import pytz

from qstrader.alpha_model.fixed_signals import FixedSignalsAlphaModel
from qstrader.asset.universe.static import StaticUniverse
from qstrader.trading.backtest import BacktestTradingSession


def test_backtest_sixty_forty_no_corp_actions(etf_filepath):
    """
    Ensures that a full end-to-end weekly rebalanced backtested
    trading session with fixed proportion weights produces the
    correct rebalance orders as well as correctly calculated
    market values after a single month's worth of daily
    backtesting.
    """
    os.environ['QSTRADER_CSV_DATA_DIR'] = etf_filepath

    assets = ['EQ:ABC', 'EQ:DEF']
    universe = StaticUniverse(assets)
    signal_weights = {'EQ:ABC': 0.6, 'EQ:DEF': 0.4}
    alpha_model = FixedSignalsAlphaModel(signal_weights)

    start_dt = pd.Timestamp('2019-01-01 00:00:00', tz=pytz.UTC)
    end_dt = pd.Timestamp('2019-01-31 23:59:00', tz=pytz.UTC)

    backtest = BacktestTradingSession(
        start_dt,
        end_dt,
        universe,
        alpha_model,
        portfolio_id='000001',
        rebalance='weekly',
        rebalance_weekday='WED',
        cash_buffer_percentage=0.05
    )
    backtest.run(results=False)

    portfolio = backtest.broker.portfolios['000001']

    portfolio_dict = portfolio.portfolio_to_dict()
    expected_dict = {
        'EQ:ABC': {
            'unrealised_pnl': -31121.26203538094,
            'realised_pnl': 0.0,
            'total_pnl': -31121.26203538094,
            'market_value': 561680.8382534103,
            'quantity': 4674
        },
        'EQ:DEF': {
            'unrealised_pnl': 18047.831359406424,
            'realised_pnl': 613.3956570402925,
            'total_pnl': 18661.227016446715,
            'market_value': 376203.80367208034,
            'quantity': 1431.0
        }
    }

    history_df = portfolio.history_to_df().reset_index()
    expected_df = pd.read_csv(os.path.join(etf_filepath, 'history.dat'))

    pd.testing.assert_frame_equal(history_df, expected_df)
    assert portfolio_dict == expected_dict
