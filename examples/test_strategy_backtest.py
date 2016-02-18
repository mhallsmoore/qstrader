from decimal import Decimal

from qstrader.backtest.backtest import Backtest
from qstrader.execution_handler.execution_handler import IBSimulatedExecutionHandler
from qstrader.portfolio_handler.portfolio_handler import PortfolioHandler
from qstrader.position_sizer.position_sizer import TestPositionSizer
from qstrader.price_handler.price_handler import HistoricCSVPriceHandler
from qstrader.risk_manager.risk_manager import TestRiskManager
from qstrader import settings
from qstrader.strategy.strategy import TestStrategy


if __name__ == "__main__":
    tickers = ["GOOG"]

    backtest = Backtest(
        tickers, HistoricCSVPriceHandler, 
        TestStrategy, PortfolioHandler, 
        IBSimulatedExecutionHandler,
        TestPositionSizer, TestRiskManager, 
        equity=Decimal("500000.00")
    )
    backtest.simulate_trading()
