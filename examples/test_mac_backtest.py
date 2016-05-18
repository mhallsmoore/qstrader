from decimal import Decimal

from qstrader.backtest.backtest import Backtest
from qstrader.execution_handler.execution_handler import IBSimulatedExecutionHandler
from qstrader.portfolio_handler.portfolio_handler import PortfolioHandler
from qstrader.position_sizer.balanced_position_sizer import BalancedPositionSizer
from qstrader.price_handler.yahoo_price_handler import YahooDailyBarPriceHandler
from qstrader.risk_manager.balanced_risk_manager import BalancedRiskManager
from qstrader.statistics.statistics import SimpleStatistics
from qstrader import settings
from qstrader.strategy.moving_average_cross_strategy import MovingAverageCrossStrategy
try:
		import Queue as queue
except ImportError:
		import queue


if __name__ == "__main__":
    tickers = ["AAPL"]

	# Set up variables needed for backtest
    events_queue = queue.Queue()
    csv_dir = settings.CSV_DATA_DIR
    initial_equity = Decimal("500000.00")
    heartbeat = 0.0
    max_iters = 10000000000
    NUM_STOCKS = 1

    # Use Yahoo Daily Price Handler
    price_handler = YahooDailyBarPriceHandler(
        csv_dir, events_queue, tickers
    )

    # Use the MAC Strategy
    strategy = MovingAverageCrossStrategy( tickers, events_queue )

    # Use an example Position Sizer, 1 stock
    position_sizer = BalancedPositionSizer(NUM_STOCKS)

    # Use a balanced Risk Manager, 1 stock
    risk_manager = BalancedRiskManager(NUM_STOCKS)

    # Use the default Portfolio Handler
    portfolio_handler = PortfolioHandler(
        initial_equity, events_queue, price_handler,
        position_sizer, risk_manager
    )
    
    # Use a simulated IB Execution Handler
    execution_handler = IBSimulatedExecutionHandler(
        events_queue, price_handler
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
    backtest.simulate_trading()