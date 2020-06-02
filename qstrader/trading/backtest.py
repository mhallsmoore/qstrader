import os

import pandas as pd

from qstrader.asset.equity import Equity
from qstrader.broker.simulated_broker import SimulatedBroker
from qstrader.broker.fee_model.zero_fee_model import ZeroFeeModel
from qstrader.data.backtest_data_handler import BacktestDataHandler
from qstrader.data.daily_bar_csv import CSVDailyBarDataSource
from qstrader.exchange.simulated_exchange import SimulatedExchange
from qstrader.simulation.daily_bday import DailyBusinessDaySimulationEngine
from qstrader.system.qts import QuantTradingSystem
from qstrader.system.rebalance.buy_and_hold import BuyAndHoldRebalance
from qstrader.system.rebalance.daily import DailyRebalance
from qstrader.system.rebalance.end_of_month import EndOfMonthRebalance
from qstrader.system.rebalance.weekly import WeeklyRebalance
from qstrader.trading.trading_session import TradingSession


DEFAULT_ACCOUNT_NAME = 'Backtest Simulated Broker Account'
DEFAULT_PORTFOLIO_ID = '000001'
DEFAULT_PORTFOLIO_NAME = 'Backtest Simulated Broker Portfolio'


class BacktestTradingSession(TradingSession):
    """
    Encaspulates a full trading simulation backtest with externally
    provided instances for each module.

    Utilises sensible defaults to allow straightforward backtesting of
    less complex trading strategies.

    Parameters
    ----------
    start_dt : `pd.Timestamp`
        The starting datetime (UTC) of the backtest.
    end_dt : `pd.Timestamp`
        The ending datetime (UTC) of the backtest.
    universe : `Universe`
        The Asset Universe to utilise for the backtest.
    alpha_model : `AlphaModel`
        The signal/forecast alpha model for the quant trading strategy.
    risk_model : `RiskModel`
        The optional risk model for the quant trading strategy.
    signals : `SignalsCollection`, optional
        An optional collection of signals used in the trading models.
    initial_cash : `float`, optional
        The initial account equity (defaults to $1MM)
    rebalance : `str`, optional
        The rebalance frequency of the backtest, defaulting to 'weekly'.
    account_name : `str`, optional
        The name of the simulated broker account.
    portfolio_id : `str`, optional
        The ID of the portfolio being used for the backtest.
    portfolio_name : `str`, optional
        The name of the portfolio being used for the backtest.
    cash_buffer_percentage : `float`, optional
        The percentage of the portfolio to retain in cash.
    fee_model : `FeeModel` class instance, optional
        The optional FeeModel derived subclass to use for transaction cost estimates.
    burn_in_dt : `pd.Timestamp`, optional
        The optional date provided to begin tracking strategy statistics,
        which is used for strategies requiring a period of data 'burn in'
    """

    def __init__(
        self,
        start_dt,
        end_dt,
        universe,
        alpha_model,
        risk_model=None,
        signals=None,
        initial_cash=1e6,
        rebalance='weekly',
        account_name=DEFAULT_ACCOUNT_NAME,
        portfolio_id=DEFAULT_PORTFOLIO_ID,
        portfolio_name=DEFAULT_PORTFOLIO_NAME,
        cash_buffer_percentage=0.05,
        fee_model=ZeroFeeModel(),
        burn_in_dt=None,
        data_handler=None,
        **kwargs
    ):
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.universe = universe
        self.alpha_model = alpha_model
        self.risk_model = risk_model
        self.signals = signals
        self.initial_cash = initial_cash
        self.rebalance = rebalance
        self.account_name = account_name
        self.portfolio_id = portfolio_id
        self.portfolio_name = portfolio_name
        self.cash_buffer_percentage = cash_buffer_percentage
        self.fee_model = fee_model
        self.burn_in_dt = burn_in_dt

        self.exchange = self._create_exchange()
        self.data_handler = self._create_data_handler(data_handler)
        self.broker = self._create_broker()
        self.sim_engine = self._create_simulation_engine()

        if rebalance == 'weekly':
            if 'rebalance_weekday' in kwargs:
                self.rebalance_weekday = kwargs['rebalance_weekday']
            else:
                raise ValueError(
                    "Rebalance frequency was set to 'weekly' but no specific "
                    "weekday was provided. Try adding the 'rebalance_weekday' "
                    "keyword argument to the instantiation of "
                    "BacktestTradingSession, e.g. with 'WED'."
                )
        self.rebalance_schedule = self._create_rebalance_event_times()

        self.qts = self._create_quant_trading_system()
        self.equity_curve = []
        self.target_allocations = []

    def _is_rebalance_event(self, dt):
        """
        Checks if the provided timestamp is part of the rebalance
        schedule of the backtest.

        Parameters
        ----------
        dt : `pd.Timestamp`
            The timestamp to check the rebalance schedule for.

        Returns
        -------
        `Boolean`
            Whether the timestamp is part of the rebalance schedule.
        """
        return dt in self.rebalance_schedule

    def _create_exchange(self):
        """
        Generates a simulated exchange instance used for
        market hours and holiday calendar checks.

        Returns
        -------
        `SimulatedExchanage`
            The simulated exchange instance.
        """
        return SimulatedExchange(self.start_dt)

    def _create_data_handler(self, data_handler):
        """
        Creates a DataHandler instance to load the asset pricing data
        used within the backtest.

        TODO: Currently defaults to CSV data sources of daily bar data in
        the YahooFinance format.

        Parameters
        ----------
        `BacktestDataHandler` or None
            The (potential) backtesting data handler instance.

        Returns
        -------
        `BacktestDataHandler`
            The backtesting data handler instance.
        """
        if data_handler is not None:
            return data_handler

        try:
            os.environ['QSTRADER_CSV_DATA_DIR']
        except KeyError:
            print(
                "The QSTRADER_CSV_DATA_DIR environment variable has not been set. "
                "This means that QSTrader will fall back to finding data within the "
                "current directory where the backtest has been executed. However "
                "it is strongly recommended that a QSTRADER_CSV_DATA_DIR environment "
                "variable is set for future backtests."
            )
            csv_dir = '.'
        else:
            csv_dir = os.environ.get('QSTRADER_CSV_DATA_DIR')

        # TODO: Only equities are supported by QSTrader for now.
        data_source = CSVDailyBarDataSource(csv_dir, Equity)

        data_handler = BacktestDataHandler(
            self.universe, data_sources=[data_source]
        )
        return data_handler

    def _create_broker(self):
        """
        Create the SimulatedBroker with an appropriate default
        portfolio identifiers.

        Returns
        -------
        `SimulatedBroker`
            The simulated broker instance.
        """
        broker = SimulatedBroker(
            self.start_dt,
            self.exchange,
            self.data_handler,
            account_id=self.account_name,
            initial_funds=self.initial_cash,
            fee_model=self.fee_model
        )
        broker.create_portfolio(self.portfolio_id, self.portfolio_name)
        broker.subscribe_funds_to_portfolio(self.portfolio_id, self.initial_cash)
        return broker

    def _create_simulation_engine(self):
        """
        Create a simulation engine instance to generate the events
        used for the quant trading algorithm to act upon.

        TODO: Currently hardcoded to daily events

        Returns
        -------
        `SimulationEngine`
            The simulation engine generating simulation timestamps.
        """
        return DailyBusinessDaySimulationEngine(
            self.start_dt, self.end_dt, pre_market=False, post_market=False
        )

    def _create_rebalance_event_times(self):
        """
        Creates the list of rebalance timestamps used to determine when
        to execute the quant trading strategy throughout the backtest.

        Returns
        -------
        `List[pd.Timestamp]`
            The list of rebalance timestamps.
        """
        if self.rebalance == 'buy_and_hold':
            rebalancer = BuyAndHoldRebalance(self.start_dt)
        elif self.rebalance == 'daily':
            rebalancer = DailyRebalance(
                self.start_dt, self.end_dt
            )
        elif self.rebalance == 'weekly':
            rebalancer = WeeklyRebalance(
                self.start_dt, self.end_dt, self.rebalance_weekday
            )
        elif self.rebalance == 'end_of_month':
            rebalancer = EndOfMonthRebalance(self.start_dt, self.end_dt)
        else:
            raise ValueError(
                'Unknown rebalance frequency "%s" provided.' % self.rebalance
            )
        return rebalancer.rebalances

    def _create_quant_trading_system(self):
        """
        Creates the quantitative trading system with the provided
        alpha model.

        TODO: All portfolio construction/optimisation is hardcoded for
        sensible defaults.

        Returns
        -------
        `QuantTradingSystem`
            The quantitative trading system.
        """
        qts = QuantTradingSystem(
            self.universe,
            self.broker,
            self.portfolio_id,
            self.data_handler,
            self.alpha_model,
            self.risk_model,
            self.cash_buffer_percentage,
            submit_orders=True
        )
        return qts

    def _update_equity_curve(self, dt):
        """
        Update the equity curve values.

        Parameters
        ----------
        dt : `pd.Timestamp`
            The time at which the total account equity is obtained.
        """
        self.equity_curve.append(
            (dt, self.broker.get_account_total_equity()["master"])
        )

    def output_holdings(self):
        """
        Output the portfolio holdings to the console.
        """
        self.broker.portfolios[self.portfolio_id].holdings_to_console()

    def get_equity_curve(self):
        """
        Returns the equity curve as a Pandas DataFrame.

        Returns
        -------
        `pd.DataFrame`
            The datetime-indexed equity curve of the strategy.
        """
        equity_df = pd.DataFrame(
            self.equity_curve, columns=['Date', 'Equity']
        ).set_index('Date')
        equity_df.index = equity_df.index.date
        return equity_df

    def get_target_allocations(self):
        """
        Returns the target allocations as a Pandas DataFrame
        utilising the same index as the equity curve with
        forward-filled dates.

        Returns
        -------
        `pd.DataFrame`
            The datetime-indexed target allocations of the strategy.
        """
        equity_curve = self.get_equity_curve()
        alloc_df = pd.DataFrame(self.target_allocations).set_index('Date')
        alloc_df.index = alloc_df.index.date
        alloc_df = alloc_df.reindex(index=equity_curve.index, method='ffill')
        if self.burn_in_dt is not None:
            alloc_df = alloc_df[self.burn_in_dt:]
        return alloc_df

    def run(self, results=False):
        """
        Execute the simulation engine by iterating over all
        simulation events, rebalancing the quant trading
        system at the appropriate schedule.

        Parameters
        ----------
        results : `Boolean`, optional
            Whether to output the current portfolio holdings
        """
        print("Beginning backtest simulation...")

        stats = {'target_allocations': []}

        for event in self.sim_engine:
            # Output the system event and timestamp
            dt = event.ts
            print("(%s) - %s" % (event.ts, event.event_type))

            # Update the simulated broker
            self.broker.update(dt)

            # Update any signals on a daily basis
            if self.signals is not None and event.event_type == "market_close":
                self.signals.update(dt)

            # If we have hit a rebalance time then carry
            # out a full run of the quant trading system
            if self._is_rebalance_event(dt):
                print("(%s) - trading logic and rebalance" % event.ts)
                self.qts(dt, stats=stats)

            # Out of market hours we want a daily
            # performance update, but only if we
            # are past the 'burn in' period
            if event.event_type == "market_close":
                if self.burn_in_dt is not None:
                    if dt >= self.burn_in_dt:
                        self._update_equity_curve(dt)
                else:
                    self._update_equity_curve(dt)

        self.target_allocations = stats['target_allocations']

        # At the end of the simulation output the
        # portfolio holdings if desired
        if results:
            self.output_holdings()

        print("Ending backtest simulation.")
