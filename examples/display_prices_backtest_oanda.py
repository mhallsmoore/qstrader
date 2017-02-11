import click
from click_datetime import Datetime

from qstrader import settings
from qstrader.compat import queue
from qstrader.price_parser import PriceParser
from qstrader.price_handler.oanda import OandaBarPriceHandler
from qstrader.strategy import DisplayStrategy
from qstrader.position_sizer.fixed import FixedPositionSizer
from qstrader.risk_manager.example import ExampleRiskManager
from qstrader.portfolio_handler import PortfolioHandler
from qstrader.compliance.example import ExampleCompliance
from qstrader.execution_handler.ib_simulated import IBSimulatedExecutionHandler
from qstrader.statistics.simple import SimpleStatistics
from qstrader.trading_session.backtest import Backtest


def run(config, testing, tickers, granularity, start_date, end_date,
        daily_alignment, alignment_timezone, filename, n, n_window):

    # Set up variables needed for backtest
    events_queue = queue.Queue()
    initial_equity = PriceParser.parse(500000.00)

    server = 'api-fxpractice.oanda.com'
    bearer_token = config.OANDA_API_ACCESS_TOKEN

    instrument = tickers[0]
    warmup_bar_count = 0

    price_handler = OandaBarPriceHandler(
        instrument, granularity,
        start_date, end_date,
        daily_alignment, alignment_timezone,
        warmup_bar_count,
        server, bearer_token,
        events_queue
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
@click.option('--tickers', default='EUR_USD', help='Instrument')
@click.option('--granularity', default='D')
@click.option('--start_date', default='2016-01-01', type=Datetime(format='%Y-%m-%d'))
@click.option('--end_date', default='2016-12-31', type=Datetime(format='%Y-%m-%d'))
@click.option('--daily_alignment', default='0')
@click.option('--alignment_timezone', default='Europe/Paris')
@click.option('--filename', default='', help='Pickle (.pkl) statistics filename')
@click.option('--n', default=100, help='Display prices every n price events')
@click.option('--n_window', default=5, help='Display n_window prices')
def main(
        config, testing, tickers, granularity, start_date, end_date,
        daily_alignment, alignment_timezone, filename, n, n_window):
    tickers = tickers.split(",")
    config = settings.from_file(config, testing)
    run(config, testing, tickers, granularity, start_date, end_date,
        daily_alignment, alignment_timezone, filename, n, n_window)


if __name__ == "__main__":
    main()
