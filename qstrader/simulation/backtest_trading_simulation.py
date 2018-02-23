# The MIT License (MIT)
#
# Copyright (c) 2015 QuantStart.com, QuarkGluon Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys

import pandas as pd
import pytz

from qstrader.exchange.equity import Equity
from qstrader.algo.fixed_weight_alpha_model import FixedWeightAlphaModel
from qstrader.algo.fixed_weight_pcm import FixedWeightPCM
from qstrader.algo.quant_trading_algo import QuantitativeTradingAlgorithm
from qstrader.algo.weekly_rebalance import WeeklyRebalance
from qstrader.broker.simulated_broker import SimulatedBroker
from qstrader.broker.zero_broker_commission import ZeroBrokerCommission
from qstrader.broker.td_direct_broker_commission import TDDirectBrokerCommission
from qstrader.exchange.csv_bar_data import CSVBarDataPriceVolumeDataSource
from qstrader.exchange.simulated_exchange import SimulatedExchange
from qstrader.simulation.daily_business_day_simulation_engine import (
    DailyBusinessDaySimulationEngine
)
from qstrader.simulation.trading_simulation import TradingSimulation
from qstrader.statistics.tearsheet_statistics import TearsheetStatistics


class BacktestTradingSimulation(TradingSimulation):
    """TODO: Fill in doc string!
    """

    def __init__(self, settings):
        self.settings = settings
        self.commission_models = self._create_commission_model_dict()
        self.alpha_models = self._create_alpha_model_dict()
        self.start_dt = self._create_start_date()
        self.end_dt = self._create_end_date()
        self.exchange_open_time_utc = self._create_exchange_open_time_utc()
        self.exchange_close_time_utc = self._create_exchange_close_time_utc()
        self.assets = self._create_assets()
        self.exchange = self._create_exchange()
        self.broker_commission = self._create_broker_commission()
        self.broker = self._create_broker()
        self.alpha_models = self._create_alpha_models()
        self.rebalance_times = self._create_rebalance_event_times()
        self.pcm = self._create_portfolio_construction()
        self.qta = self._create_quant_trading_algo()
        self.sim_engine = self._create_simulation_engine()
        self.statistics = self._create_statistics()

    def _create_commission_model_dict(self):
        """
        Creates the mapping between user input broker commission
        choices and the class name.
        """
        return {
            "Zero": ZeroBrokerCommission,
            "TD Direct": TDDirectBrokerCommission
        }

    def _create_alpha_model_dict(self):
        """
        Creates the mapping between user input alpha model
        choices and the class name.
        """
        return {
            "Fixed Weight": FixedWeightAlphaModel
        }

    def _create_start_date(self):
        """
        Set the starting timestamp of the backtest simulation in UTC.
        """
        return pd.Timestamp(
            self.settings.SIMULATION['START_DATE'], tz=pytz.UTC
        )

    def _create_end_date(self):
        """
        Set the ending timestamp of the backtest simulation in UTC.
        """
        return pd.Timestamp(
            self.settings.SIMULATION['END_DATE'], tz=pytz.UTC
        )

    def _create_exchange_open_time_utc(self):
        """
        Set the exchange daily opening time of the backtest simulation
        in UTC.
        """
        return pd.Timestamp(
            self.settings.EXCHANGE['OPENING_UTC'],
            tz=pytz.timezone(self.settings.EXCHANGE['TIMEZONE'])
        ).tz_convert("UTC")

    def _create_exchange_close_time_utc(self):
        """
        Set the exchange daily closing time of the backtest simulation
        in UTC.
        """
        return pd.Timestamp(
            self.settings.EXCHANGE['CLOSING_UTC'],
            tz=pytz.timezone(self.settings.EXCHANGE['TIMEZONE'])
        ).tz_convert("UTC")

    def _create_assets(self):
        """
        Load in the list of specified assets. Currently hardcoded
        as Equity assets.

        TODO: In later versions, eliminate hardcoding of Equity
        """
        tickers = self.settings.DATA['ASSETS']
        assets = [
            Equity(ticker, ticker, None, tax_exempt=True)
            for ticker in tickers
        ]
        return assets

    def _create_exchange(self):
        """
        Create a SimulatedExchange with the appropriate CSV Data sources
        """
        csv_dir = os.path.join(os.getcwd(), self.settings.DATA['ROOT'])
        data_sources = [
            CSVBarDataPriceVolumeDataSource(
                asset, self.exchange_open_time_utc,
                self.exchange_close_time_utc, csv_dir,
                "%s.csv" % asset.symbol
            ) for asset in self.assets
        ]
        return SimulatedExchange(self.start_dt, data_sources)

    def _create_broker_commission(self):
        """
        Create the broker commission instance, if supported.
        """
        comm_model = self.settings.BROKER['COMMISSION']['MODEL']
        if comm_model in self.commission_models:
            broker_commission = self.commission_models[comm_model]()
        else:
            print(
                "No supported Broker Commission "
                "model specified. Exiting."
            )
            sys.exit()
        return broker_commission

    def _create_broker(self):
        """
        Create the SimulatedBroker with an appropriate default
        portfolio as given in the configuration.
        """
        acct_name = self.settings.BROKER['ACCOUNT_NAME']
        init_cash = self.settings.BROKER['INITIAL_CASH']
        self.portfolio_id = self.settings.BROKER['PORTFOLIO_ID']
        self.portfolio_name = self.settings.BROKER['PORTFOLIO_NAME']
        broker = SimulatedBroker(
            self.start_dt, self.exchange,
            account_id=acct_name,
            initial_funds=init_cash,
            broker_commission=self.broker_commission
        )
        broker.create_portfolio(self.portfolio_id, self.portfolio_name)
        broker.subscribe_funds_to_portfolio(self.portfolio_id, init_cash)
        return broker

    def _create_alpha_models(self):
        """
        Creates a set of FixedWeightAlphaModel instances if the user
        has specified 'Fixed Weight' in the configuration file.

        TODO: Eliminate the hardcoded alpha model here.
        """
        if self.settings.SIMULATION['ALPHA']['MODEL'] == "Fixed Weight":
            alpha_model = FixedWeightAlphaModel
        else:
            print("No supported Alpha Model model specified. Exiting.")
            sys.exit()
        alpha_models = [
            alpha_model(
                asset, self.start_dt,
                self.settings.SIMULATION['ALPHA']['WEIGHTS']
            ) for asset in self.assets
        ]
        return alpha_models

    def _create_rebalance_event_times(self):
        """
        TODO: Fill in doc string!
        """
        reb = WeeklyRebalance(self.start_dt, self.end_dt, 'WED')
        return reb.output_rebalances()

    def _create_portfolio_construction(self):
        """
        TODO: Fill in doc string!
        """
        pcm = FixedWeightPCM(
            self.start_dt, self.broker, self.portfolio_id,
            transaction_cost_model=self.broker_commission,
            rebalance_times=self.rebalance_times,
            adjustment_factor=0.99  # TODO: Do not hardcode this
        )
        return pcm

    def _create_quant_trading_algo(self):
        """
        Create the quant trading algo code which ties together the
        alpha model and portfolio construction to generate orders
        for a broker.
        """
        qta = QuantitativeTradingAlgorithm(
            self.start_dt, self.broker, self.portfolio_id,
            self.alpha_models, self.pcm
        )
        return qta

    def _create_simulation_engine(self):
        """
        Create a simulation engine instance to generate the events
        used for the quant trading algorithm to act upon.

        TODO: Currently hardcoded to daily events
        """
        sim_engine = DailyBusinessDaySimulationEngine(
            self.start_dt, self.end_dt
        )
        return sim_engine

    def _create_statistics(self):
        """
        Create a statistics instance to process the results of the
        trading backtest.
        """
        statistics = TearsheetStatistics(
            self.broker, title=self.settings.SIMULATION['TITLE']
        )
        return statistics

    def output_holdings(self):
        """
        Output the portfolio holdings to the console.
        """
        self.broker.portfolios[self.portfolio_id].holdings_to_console()

    def output_portfolio_history(self):
        """
        Output the portfolio transaction history.
        """
        hist_df = self.broker.portfolios[
            self.portfolio_id
        ].history_to_df()
        print(hist_df)

    def run(self):
        """
        Loop over all simulation events, update the time and subsequently
        update the exchange, broker and quant algorithm logic to generate
        new orders. At the end of each trading day, calculate performance
        and add to the statistics instance. At the end of the simulation
        output the results of the simulation via a simple plot.
        """
        for event in self.sim_engine:
            dt = event.ts
            self.exchange.update(dt)
            self.broker.update(dt)
            self.qta.update(dt)
            if event.event_type == "post_market":
                self.statistics.update(dt)
        self.statistics.plot_results()
