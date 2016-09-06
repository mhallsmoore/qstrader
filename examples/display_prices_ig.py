import click

from qstrader import settings
from qstrader.compat import queue
from qstrader.price_parser import PriceParser
from qstrader.price_handler.ig import IGTickPriceHandler
from qstrader.strategy import DisplayStrategy
from qstrader.position_sizer.fixed import FixedPositionSizer
from qstrader.risk_manager.example import ExampleRiskManager
from qstrader.portfolio_handler import PortfolioHandler
from qstrader.compliance.example import ExampleCompliance
from qstrader.execution_handler.ib_simulated import IBSimulatedExecutionHandler
from qstrader.statistics.simple import SimpleStatistics
from qstrader.trading_session.backtest import Backtest

from trading_ig import (IGService, IGStreamService)


def run(config, testing, tickers, filename, n, n_window):

    # Set up variables needed for backtest
    events_queue = queue.Queue()

    ig_service = IGService(config.IG.USERNAME, config.IG.PASSWORD, config.IG.API_KEY, config.IG.ACCOUNT.TYPE)

    ig_stream_service = IGStreamService(ig_service)
    ig_session = ig_stream_service.create_session()
    accountId = ig_session[u'accounts'][0][u'accountId']

    ig_stream_service.connect(accountId)

    initial_equity = PriceParser.parse(500000.00)

    # Use IG Tick Price Handler
    price_handler = IGTickPriceHandler(
        events_queue, ig_stream_service, tickers
    )

    # Use the Display Strategy
    strategy = DisplayStrategy(n=n, n_window=n_window)

    # Use an example Position Sizer
    position_sizer = FixedPositionSizer()

    # Use an example Risk Manager
    risk_manager = ExampleRiskManager()

    # Use the default Portfolio Handler
    portfolio_handler = PortfolioHandler(
        initial_equity, events_queue, price_handler,
        position_sizer, risk_manager
    )

    # Use the ExampleCompliance component
    compliance = ExampleCompliance(config)

    # Use a simulated IB Execution Handler
    execution_handler = IBSimulatedExecutionHandler(
        events_queue, price_handler, compliance
    )

    # Use the default Statistics
    statistics = SimpleStatistics(config, portfolio_handler)

    # Set up the backtest
    backtest = Backtest(
        price_handler, strategy,
        portfolio_handler, execution_handler,
        position_sizer, risk_manager,
        statistics, initial_equity
    )
    results = backtest.simulate_trading(testing=testing)
    statistics.save(filename)
    return results


@click.command()
@click.option('--config', default=settings.DEFAULT_CONFIG_FILENAME, help='Config filename')
@click.option('--testing/--no-testing', default=False, help='Enable testing mode')
@click.option('--tickers', default='L1:CS.D.GBPUSD.CFD.IP,L1:CS.D.USDJPY.CFD.IP', help='Tickers (use comma)')
@click.option('--filename', default='', help='Pickle (.pkl) statistics filename')
@click.option('--n', default=1, help='Display prices every n price events')
@click.option('--n_window', default=5, help='Display n_window prices')
def main(config, testing, tickers, filename, n, n_window):
    tickers = tickers.split(",")
    config = settings.from_file(config, testing)
    run(config, testing, tickers, filename, n, n_window)


if __name__ == "__main__":
    main()
