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
        account_name='Strategic Asset Allocation Account',
        portfolio_id='SAA001',
        portfolio_name='Strategic Asset Allocation - 60/40 US Equities/Bonds (SPY/AGG)',
        cash_buffer_percentage=0.05
    )
    backtest.run()
