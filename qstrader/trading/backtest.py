import os

from qstrader.asset.equity import Equity
from qstrader.asset.universe.static import StaticUniverse
from qstrader.broker.simulated_broker import SimulatedBroker
from qstrader.broker.fee_model.zero_fee_model import ZeroFeeModel
from qstrader.data.backtest_data_handler import BacktestDataHandler
from qstrader.data.daily_bar_csv import CSVDailyBarDataSource
from qstrader.exchange.simulated_exchange import SimulatedExchange
from qstrader.simulation.daily_bday import DailyBusinessDaySimulationEngine
from qstrader.statistics.tearsheet import TearsheetStatistics
from qstrader.system.qts import QuantTradingSystem
from qstrader.system.rebalance.buy_and_hold import BuyAndHoldRebalance
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
    assets : `List[str]`
        The Asset symbols to utilise for the backtest.
    alpha_model : `AlphaModel`
        The signal/forecast alpha model for the quant trading strategy.
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
    fees : `FeeModel` class (not instance), optional
        The optional FeeModel class to use for transaction cost estimates.
        TODO: FeeModels are currently not supported.
    """

    def __init__(
        self,
        start_dt,
        end_dt,
        assets,
        alpha_model,
        initial_cash=1e6,
        rebalance='weekly',
        account_name=DEFAULT_ACCOUNT_NAME,
        portfolio_id=DEFAULT_PORTFOLIO_ID,
        portfolio_name=DEFAULT_PORTFOLIO_NAME,
        cash_buffer_percentage=0.05,
        fees=None,
        **kwargs
    ):
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.assets = assets
        self.alpha_model = alpha_model
        self.initial_cash = initial_cash
        self.rebalance = rebalance
        self.account_name = account_name
        self.portfolio_id = portfolio_id
        self.portfolio_name = portfolio_name
        self.cash_buffer_percentage = cash_buffer_percentage
        self.fees = fees

        self.exchange = self._create_exchange()
        self.universe = self._create_asset_universe()
        self.data_handler = self._create_data_handler()
        self.fee_model = self._create_broker_fee_model()
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

        # Create the full quantitative trading system
        self.qts = self._create_quant_trading_system()

        # Performance output
        self.statistics = self._create_statistics()

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

    def _create_asset_universe(self):
        """
        Check all asset symbols to ensure they are supported by QSTrader and
        then create an asset Universe instance.

        TODO: Currently this only supports StaticUniverse instances.

        Returns
        -------
        `Universe`
            The asset universe generated from the asset symbols.
        """
        # Check that all provided asset symbols are equities.
        for asset in self.assets:
            if not asset.startswith('EQ'):
                raise NotImplementedError(
                    'QSTrader currently only supports Equity assets and '
                    'not provided asset "%s". Perhaps you need to prefix the '
                    'asset symbol name with "EQ:" in your asset list?' % asset
                )

        universe = StaticUniverse(self.assets)
        return universe

    def _create_data_handler(self):
        """
        Creates a DataHandler instance to load the asset pricing data
        used within the backtest.

        TODO: Currently defaults to CSV data sources of daily bar data in
        the YahooFinance format.

        Returns
        -------
        `BacktestDataHandler`
            The backtesting data handler instance.
        """
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

    def _create_broker_fee_model(self):
        """
        Create the broker fee model instance, if supported.

        TODO: Only supporting ZeroFeeModel for the time being.

        Returns
        -------
        `FeeModel`
            The brokerage simulated fee model.
        """
        return ZeroFeeModel

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
            self.start_dt, self.end_dt
        )

    def _create_rebalance_event_times(self):
        """
        Creates the list of rebalance timestamps used to determine when
        to execute the quant trading strategy throughout the backtest.

        TODO: Currently supports only weekly rebalances.

        Returns
        -------
        `List[pd.Timestamp]`
            The list of rebalance timestamps.
        """
        if self.rebalance == 'buy_and_hold':
            rebalancer = BuyAndHoldRebalance(self.start_dt)
        elif self.rebalance == 'daily':
            raise NotImplementedError(
                'QSTrader does not yet support daily rebalancing.'
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
            self.cash_buffer_percentage,
            submit_orders=True
        )
        return qts

    def _create_statistics(self):
        """
        Create a statistics instance to process the results of the
        trading backtest.

        Returns
        -------
        `TearsheetStatistics`
            The tearsheet statistics instance.
        """
        return TearsheetStatistics(self.broker, title=self.portfolio_name)

    def output_holdings(self):
        """
        Output the portfolio holdings to the console.
        """
        self.broker.portfolios[self.portfolio_id].holdings_to_console()

    def run(self, results=True):
        """
        Execute the simulation engine by iterating over all
        simulation events, rebalancing the quant trading
        system at the appropriate schedule.
        """
        for event in self.sim_engine:
            # Output the system event and timestamp
            dt = event.ts
            print(event.ts, event.event_type)

            # Update the simulated broker
            self.broker.update(dt)

            # If we have hit a rebalance time then carry
            # out a full run of the quant trading system
            if self._is_rebalance_event(dt):
                print(event.ts, "REBALANCE")
                self.qts(dt)

            # Out of market hours we want a daily
            # performance update
            if event.event_type == "post_market":
                self.statistics.update(dt)

        # At the end of the simulation output the
        # holdings and plot the tearsheet
        if results:
            self.output_holdings()
            self.statistics.plot_results()
