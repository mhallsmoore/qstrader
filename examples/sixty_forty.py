import pandas as pd
import pytz

from qstrader.alpha_model.fixed_signals import FixedSignalsAlphaModel
from qstrader.trading.backtest import BacktestTradingSession


if __name__ == "__main__":
    assets = ['EQ:SPY', 'EQ:AGG']
    signal_weights = {'EQ:SPY': 0.6, 'EQ:AGG': 0.4}
    alpha_model = FixedSignalsAlphaModel(signal_weights)

    start_dt = pd.Timestamp('2004-01-01 00:00:00', tz=pytz.UTC)
    end_dt = pd.Timestamp('2018-12-31 23:59:00', tz=pytz.UTC)

    backtest = BacktestTradingSession(
        start_dt,
        end_dt,
        assets,
        alpha_model,
        rebalance='end_of_month',
    )
    backtest.run()
