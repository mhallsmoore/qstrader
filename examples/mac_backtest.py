import click

from decimal import Decimal

from qstrader import settings
from qstrader.compat import queue
from qstrader.price_handler.yahoo_daily_csv_bar import YahooDailyCsvBarPriceHandler
from qstrader.strategy.moving_average_cross_strategy import MovingAverageCrossStrategy
from qstrader.position_sizer.fixed import FixedPositionSizer
from qstrader.risk_manager.example import ExampleRiskManager
from qstrader.portfolio_handler import PortfolioHandler
from qstrader.compliance.csv import CsvCompliance
from qstrader.execution_handler.ib_simulated import IBSimulatedExecutionHandler
from qstrader.statistics.simple import SimpleStatistics
from qstrader.trading_session.backtest import Backtest


def run(config, testing):
    tickers = ["SP500TR"]

    # Set up variables needed for backtest
    events_queue = queue.Queue()
    csv_dir = config.CSV_DATA_DIR
    initial_equity = Decimal("500000.00")
    # heartbeat = 0.0
    # max_iters = 10000000000

    # Use Yahoo Daily Price Handler
    price_handler = YahooDailyCsvBarPriceHandler(
        csv_dir, events_queue, tickers
    )

    # Use the MAC Strategy
    strategy = MovingAverageCrossStrategy(tickers, events_queue)

    # Use an example Position Sizer,
    position_sizer = FixedPositionSizer()

    # Use an example Risk Manager,
    risk_manager = ExampleRiskManager()

    # Use the default Portfolio Handler
    portfolio_handler = PortfolioHandler(
        initial_equity, events_queue, price_handler,
        position_sizer, risk_manager
    )

    # Use the CsvCompliance component
    compliance = CsvCompliance(config)

    # Use a simulated IB Execution Handler
    execution_handler = IBSimulatedExecutionHandler(
        events_queue, price_handler, compliance
    )

    # Use the default Statistics
    statistics = SimpleStatistics(portfolio_handler)

    # Set up the backtest
    backtest = Backtest(
        tickers, price_handler,
        strategy, portfolio_handler,
        execution_handler,
        position_sizer, risk_manager,
        statistics,
        initial_equity
    )
    results = backtest.simulate_trading(testing=testing)
    return results


@click.command()
@click.option('--config', default=settings.DEFAULT_CONFIG_FILENAME, help='Config filename')
@click.option('--testing/--no-testing', default=False, help='Enable testing mode')
def main(config, testing):
    config = settings.from_file(config, testing)
    run(config, testing)

if __name__ == "__main__":
    main()
