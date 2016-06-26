from __future__ import print_function

import time
from decimal import Decimal

from qstrader.compat.compat import queue


class Backtest(object):
    """
    Enscapsulates the settings and components for
    carrying out an event-driven backtest.
    """
    def __init__(
        self, tickers, price_handler,
        strategy, portfolio_handler,
        execution_handler,
        position_sizer, risk_manager,
        statistics,
        equity=Decimal("100000.00"),
        heartbeat=0.0, max_iters=10000000000
    ):
        """
        Set up the backtest variables according to
        what has been passed in.
        """

        self.tickers = tickers
        self.price_handler = price_handler
        self.strategy = strategy
        self.portfolio_handler = portfolio_handler
        self.execution_handler = execution_handler
        self.position_sizer = position_sizer
        self.risk_manager = risk_manager
        self.statistics = statistics
        self.equity = equity
        self.heartbeat = heartbeat
        self.max_iters = max_iters
        self.events_queue = price_handler.events_queue
        self.cur_time = None

    def _run_backtest(self):
        """
        Carries out an infinite while loop that polls the
        events queue and directs each event to either the
        strategy component of the execution handler. The
        loop will then pause for "heartbeat" seconds and
        continue unti the maximum number of iterations is
        exceeded.
        """
        print("Running Backtest...")
        iters = 0
        while iters < self.max_iters and self.price_handler.continue_backtest:
            try:
                event = self.events_queue.get(False)
            except queue.Empty:
                if self.price_handler.type == "TICK_HANDLER":
                    self.price_handler.stream_next_tick()
                else:
                    self.price_handler.stream_next_bar()
            else:
                if event is not None:
                    if event.type in ['TICK', 'BAR']:
                        self.cur_time = event.time
                        self.strategy.calculate_signals(event)
                        self.portfolio_handler.portfolio._reset_values()
                        self.portfolio_handler.update_portfolio_value()
                        self.statistics.update(event.time)
                    elif event.type == 'SIGNAL':
                        self.portfolio_handler.on_signal(event)
                    elif event.type == 'ORDER':
                        self.execution_handler.execute_order(event)
                    elif event.type == 'FILL':
                        self.portfolio_handler.on_fill(event)
            time.sleep(self.heartbeat)
            iters += 1

    def simulate_trading(self, testing=False):
        """
        Simulates the backtest and outputs portfolio performance.
        """
        self._run_backtest()
        results = self.statistics.get_results()
        print("Backtest complete.")
        print("Sharpe Ratio: %s" % results["sharpe"])
        print("Max Drawdown: %s" % results["max_drawdown"])
        print("Max Drawdown Pct: %s" % results["max_drawdown_pct"])
        if not testing:
            self.statistics.plot_results()
