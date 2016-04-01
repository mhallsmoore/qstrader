from __future__ import print_function

from decimal import Decimal
import os, os.path
import pprint
try:
    import Queue as queue
except ImportError:
    import queue
import time

try:
    from qstrader import settings
except ImportError:
    print(
        "Could not import settings.py. Have you copied " \
        "settings.py.example to settings.py and configured " \
        "your QSTrader settings?"
    )


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
        equity=Decimal("100000.00"), 
        heartbeat=0.0, max_iters=10000000000
    ):
        """
        Initialises the backtest.
        """
        self.tickers = tickers
        self.events_queue = queue.Queue()
        self.csv_dir = settings.CSV_DATA_DIR
        self.output_dir = settings.OUTPUT_DIR
        self.equity_file = os.path.join(
            self.output_dir, "equity.csv"
        )

        self.price_handler = price_handler(
            self.csv_dir, self.events_queue, 
            init_tickers=self.tickers
        )
        self.strategy = strategy(
            self.tickers, self.events_queue
        )
        self.equity = equity
        self.heartbeat = heartbeat
        self.max_iters = max_iters

        self.position_sizer = position_sizer()
        self.risk_manager = risk_manager()

        self.portfolio_handler = portfolio_handler(
            self.equity, self.events_queue, self.price_handler,
            self.position_sizer, self.risk_manager
        )
        self.execution_handler = execution_handler(
            self.events_queue, self.price_handler
        )

        self.cur_time = None

        # Open the equity file and clear it prior to append
        open(self.equity_file, 'w').close()

    def _append_equity_state(self):
        cur_port_state = self.portfolio_handler.portfolio.create_portfolio_state_dict()
        with open(self.equity_file, "a") as eqfile:
            eqfile.write(
                "%s,%s\n" % (
                    self.cur_time, cur_port_state["equity"]
                )
            )

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
        ticks = 0
        while iters < self.max_iters and self.price_handler.continue_backtest:
            try:
                event = self.events_queue.get(False)
            except queue.Empty:
                self.price_handler.stream_next_tick()
            else:
                if event is not None:
                    if event.type == 'TICK':
                        self.cur_time = event.time
                        print("Tick %s, at %s" % (ticks, self.cur_time))
                        self._append_equity_state()
                        self.strategy.calculate_signals(event)
                        ticks += 1
                    elif event.type == 'SIGNAL':
                        self.portfolio_handler.on_signal(event)
                    elif event.type == 'ORDER':
                        self.execution_handler.execute_order(event)
                    elif event.type == 'FILL':
                        self.portfolio_handler.on_fill(event)
            time.sleep(self.heartbeat)
            iters += 1

    def simulate_trading(self):
        """
        Simulates the backtest and outputs portfolio performance.
        """
        self._run_backtest()
        print("Backtest complete.")
