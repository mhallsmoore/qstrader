import pandas as pd
import pytz

from qstrader.alpha_model.fixed_signals import FixedSignalsAlphaModel
from qstrader.statistics.tearsheet import TearsheetStatistics
from qstrader.trading.backtest import BacktestTradingSession


if __name__ == "__main__":
    start_dt = pd.Timestamp('2004-01-01 00:00:00', tz=pytz.UTC)
    end_dt = pd.Timestamp('2018-12-31 23:59:00', tz=pytz.UTC)

    # Strategic Asset Allocation - Fixed Weight 60/40 SPY/AGG
    strategy_assets = ['EQ:SPY', 'EQ:AGG']
    strategy_signal_weights = {'EQ:SPY': 0.6, 'EQ:AGG': 0.4}
    strategy_title = 'Strategic Asset Allocation - 60/40 US Equities/Bonds (SPY/AGG)'
    strategy_alpha_model = FixedSignalsAlphaModel(strategy_signal_weights)
    strategy_backtest = BacktestTradingSession(
        start_dt,
        end_dt,
        strategy_assets,
        strategy_alpha_model,
        rebalance='end_of_month',
        account_name='Strategic Asset Allocation Account',
        portfolio_id='SAA001',
        portfolio_name=strategy_title,
        cash_buffer_percentage=0.05
    )
    strategy_backtest.run()

    # Benchmark - Buy & Hold SPY
    benchmark_assets = ['EQ:SPY']
    benchmark_signal_weights = {'EQ:SPY': 1.0}
    benchmark_alpha_model = FixedSignalsAlphaModel(benchmark_signal_weights)
    benchmark_backtest = BacktestTradingSession(
        start_dt,
        end_dt,
        benchmark_assets,
        benchmark_alpha_model,
        account_name='Benchmark Account',
        portfolio_id='SPY001',
        portfolio_name='Benchmark - Buy & Hold S&P500 (SPY)',
        rebalance='buy_and_hold',
        cash_buffer_percentage=0.05
    )
    benchmark_backtest.run()

    # Performance Output
    tearsheet = TearsheetStatistics(
        strategy_equity=strategy_backtest.get_equity_curve(),
        benchmark_equity=benchmark_backtest.get_equity_curve(),
        title=strategy_title
    )
    tearsheet.plot_results()
