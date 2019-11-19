import os

import pandas as pd
import pytz

from qstrader.alpha_model.fixed_signals import FixedSignalsAlphaModel
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
    signal_weights = {'EQ:ABC': 0.6, 'EQ:DEF': 0.4}
    alpha_model = FixedSignalsAlphaModel(signal_weights)

    start_dt = pd.Timestamp('2019-01-01 00:00:00', tz=pytz.UTC)
    end_dt = pd.Timestamp('2019-01-31 23:59:00', tz=pytz.UTC)

    backtest = BacktestTradingSession(
        start_dt,
        end_dt,
        assets,
        alpha_model,
        rebalance='weekly',
    )
    backtest.run(results=False)

    portfolio = backtest.broker.portfolios['000001']

    portfolio_dict = portfolio.portfolio_to_dict()
    expected_dict = {
        'EQ:ABC': {
            'book_cost': 592802.1002887912,
            'gain': -31121.262035380933,
            'market_value': 561680.8382534103,
            'perc_gain': -5.249856911812527,
            'quantity': 4674.0
        },
        'EQ:DEF': {
            'book_cost': 358155.9723126739,
            'gain': 18047.83135940641,
            'market_value': 376203.80367208034,
            'perc_gain': 5.03909825735098,
            'quantity': 1431.0
        }
    }

    history_df = portfolio.history_to_df().reset_index()
    expected_df = pd.read_csv(os.path.join(etf_filepath, 'history.dat'))

    pd.testing.assert_frame_equal(history_df, expected_df)
    assert portfolio_dict == expected_dict
