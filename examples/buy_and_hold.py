import pandas as pd
import pytz

from qstrader.alpha_model.fixed_signals import FixedSignalsAlphaModel
from qstrader.trading.backtest import BacktestTradingSession


if __name__ == "__main__":
    assets = ['EQ:GLD']
    signal_weights = {'EQ:GLD': 1.0}
    alpha_model = FixedSignalsAlphaModel(signal_weights)

    start_dt = pd.Timestamp('2004-11-19 00:00:00', tz=pytz.UTC)
    end_dt = pd.Timestamp('2019-10-16 23:59:00', tz=pytz.UTC)

    backtest = BacktestTradingSession(
        start_dt,
        end_dt,
        assets,
        alpha_model,
        rebalance='buy_and_hold',
    )
    backtest.run()
