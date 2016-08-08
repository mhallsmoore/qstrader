import click

import os
from collections import OrderedDict
import pandas as pd

from qstrader import settings
from qstrader.compat import queue
from qstrader.price_parser import PriceParser
from qstrader.price_handler import GenericPriceHandler
from qstrader.price_handler.iterator.pandas import PandasTickEventIterator
from qstrader.strategy import DisplayStrategy, Strategies
from qstrader.strategy.example import ExampleStrategy
from qstrader.position_sizer.fixed import FixedPositionSizer
from qstrader.risk_manager.example import ExampleRiskManager
from qstrader.portfolio_handler import PortfolioHandler
from qstrader.compliance.example import ExampleCompliance
from qstrader.execution_handler.ib_simulated import IBSimulatedExecutionHandler
from qstrader.statistics.simple import SimpleStatistics
from qstrader.trading_session.backtest import Backtest


def run(config, testing, tickers, filename, n, n_window):

    # Set up variables needed for backtest
    events_queue = queue.Queue()
    csv_dir = config.CSV_DATA_DIR
    initial_equity = PriceParser.parse(500000.00)

    d_tickers = OrderedDict()
    for ticker in tickers:
        ticker_path = os.path.join(csv_dir, "%s.csv" % ticker)
        df = pd.io.parsers.read_csv(
            ticker_path, header=0, parse_dates=True,
            dayfirst=True, index_col=1,
            names=("Ticker", "Time", "Bid", "Ask")
        )
        del df["Ticker"]
        d_tickers[ticker] = df
    if len(tickers) == 1:
        ticker = tickers[0]
        data = d_tickers[ticker]
    else:
        data = pd.Panel.from_dict(d_tickers)
        data = data.transpose(2, 1, 0)
    print(data)
    print("Null:")
    print(data.isnull().sum())

    # Use Generic Tick Handler with Pandas Tick Iterator
    price_event_iterator = PandasTickEventIterator(data, tickers[0])
    price_handler = GenericPriceHandler(events_queue, price_event_iterator)

    # Use the Display Strategy and ExampleStrategy
    strategy1 = DisplayStrategy(n=n, n_window=n_window)
    strategy2 = ExampleStrategy(tickers, events_queue)
    strategy = Strategies(strategy1, strategy2)
    # strategy = ExampleStrategy(tickers, events_queue)

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
@click.option('--tickers', default='GOOG', help='Tickers (use comma)')
@click.option('--filename', default='', help='Pickle (.pkl) statistics filename')
@click.option('--n', default=100, help='Display prices every n price events')
@click.option('--n_window', default=5, help='Display n_window prices')
def main(config, testing, tickers, filename, n, n_window):
    tickers = tickers.split(",")
    config = settings.from_file(config, testing)
    run(config, testing, tickers, filename, n, n_window)


if __name__ == "__main__":
    main()
