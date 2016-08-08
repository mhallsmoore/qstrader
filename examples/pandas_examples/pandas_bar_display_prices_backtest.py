import click

import os
import pandas as pd
import requests_cache
import pandas_datareader.data as web

from qstrader import settings
from qstrader.compat import queue
from qstrader.price_parser import PriceParser
from qstrader.price_handler import GenericPriceHandler
from qstrader.price_handler.iterator.pandas import PandasBarEventIterator
from qstrader.strategy import DisplayStrategy, Strategies
from qstrader.strategy.buy_and_hold import BuyAndHoldStrategy
from qstrader.position_sizer.fixed import FixedPositionSizer
from qstrader.risk_manager.example import ExampleRiskManager
from qstrader.portfolio_handler import PortfolioHandler
from qstrader.compliance.example import ExampleCompliance
from qstrader.execution_handler.ib_simulated import IBSimulatedExecutionHandler
from qstrader.statistics.simple import SimpleStatistics
from qstrader.trading_session.backtest import Backtest


def init_session(cache_name, cache_backend, expire_after):
    if expire_after == '0':
        expire_after = None
        print("expire_after==0 no cache")
        return None
    else:
        if expire_after == '-1':
            expire_after = 0
            print("Installing cache '%s.sqlite' without expiration" % cache_name)
        else:
            expire_after = pd.to_timedelta(expire_after, unit='s')
            print("Installing cache '%s.sqlite' with expire_after=%s (d days hh:mm:ss)" % (cache_name, expire_after))
        session = requests_cache.CachedSession(cache_name=cache_name, backend=cache_backend, expire_after=expire_after)
        return session


def run(cache_name, cache_backend, expire_after, data_source, start, end, config, testing, tickers, filename, n, n_window):

    # Set up variables needed for backtest
    events_queue = queue.Queue()
    initial_equity = PriceParser.parse(500000.00)

    session = init_session(cache_name, cache_backend, expire_after)

    period = 86400  # Seconds in a day

    if len(tickers) == 1:
        data = web.DataReader(tickers[0], data_source, start, end, session=session)
    else:
        data = web.DataReader(tickers, data_source, start, end, session=session)

    # Use Generic Bar Handler with Pandas Bar Iterator
    price_event_iterator = PandasBarEventIterator(data, period, tickers[0])
    price_handler = GenericPriceHandler(events_queue, price_event_iterator)

    # Use the Display Strategy
    strategy1 = DisplayStrategy(n=n, n_window=n_window)
    strategy2 = BuyAndHoldStrategy(tickers, events_queue)
    strategy = Strategies(strategy1, strategy2)

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
@click.option('--max_rows', default=20, help='Maximum number of rows displayed')
@click.option('--cache_name', default='', help="Cache name (file if backend is sqlite)")
@click.option('--cache_backend', default='sqlite', help="Cache backend - default 'sqlite'")
@click.option('--expire_after', default='24:00:00.0', help=u"Cache expiration (0: no cache, -1: no expiration, d: d seconds expiration cache)")
@click.option('--data_source', default='yahoo', help='the data source ("yahoo", "yahoo-actions", "yahoo-dividends", "google", "fred", "ff", or "edgar-index")')
@click.option('--start', default='2010-01-04', help='Start')
@click.option('--end', default='2016-06-22', help='End')
@click.option('--config', default=settings.DEFAULT_CONFIG_FILENAME, help='Config filename')
@click.option('--testing/--no-testing', default=False, help='Enable testing mode')
@click.option('--tickers', default='^GSPC', help='Tickers (use comma) - default is "^GSPC" ie "SP500"')
@click.option('--filename', default='', help='Pickle (.pkl) statistics filename')
@click.option('--n', default=100, help='Display prices every n price events')
@click.option('--n_window', default=5, help='Display n_window prices')
def main(max_rows, cache_name, cache_backend, expire_after, data_source, start, end, config, testing, tickers, filename, n, n_window):
    pd.set_option('max_rows', max_rows)
    if cache_name == '':
        cache_name = "requests_cache"
    else:
        if cache_backend.lower() == 'sqlite':
            cache_name = os.path.expanduser(cache_name)
    tickers = tickers.split(",")
    config = settings.from_file(config, testing)
    run(cache_name, cache_backend, expire_after, data_source, start, end, config, testing, tickers, filename, n, n_window)


if __name__ == "__main__":
    main()
