import click

from decimal import Decimal

from qstrader.backtest.backtest import Backtest
from qstrader.execution_handler.execution_handler import IBSimulatedExecutionHandler
from qstrader.portfolio_handler.portfolio_handler import PortfolioHandler
from qstrader.position_sizer.position_sizer import TestPositionSizer
from qstrader.price_handler.yahoo_price_handler import YahooDailyBarPriceHandler
from qstrader.risk_manager.risk_manager import TestRiskManager
from qstrader.statistics.statistics import SimpleStatistics
from qstrader.compliance.compliance import TestCompliance
from qstrader import settings
from qstrader.strategy.moving_average_cross_strategy import MovingAverageCrossStrategy
from qstrader.compat.compat import queue


def run(config, testing):
    tickers = ["SP500TR"]

    # Set up variables needed for backtest
    events_queue = queue.Queue()
    csv_dir = config.CSV_DATA_DIR
    initial_equity = Decimal("500000.00")
    # heartbeat = 0.0
    # max_iters = 10000000000

    # Use Yahoo Daily Price Handler
    price_handler = YahooDailyBarPriceHandler(
        csv_dir, events_queue, tickers
    )

    # Use the MAC Strategy
    strategy = MovingAverageCrossStrategy(tickers, events_queue)

    # Use an example Position Sizer,
    position_sizer = TestPositionSizer()

    # Use an example Risk Manager,
    risk_manager = TestRiskManager()

    # Use the default Portfolio Handler
    portfolio_handler = PortfolioHandler(
        initial_equity, events_queue, price_handler,
        position_sizer, risk_manager
    )

    # Use the TestCompliance component
    compliance = TestCompliance(config)

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
