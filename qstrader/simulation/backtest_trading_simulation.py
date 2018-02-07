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
from qstrader.broker.simulated_broker import SimulatedBroker
from qstrader.broker.zero_broker_commission import ZeroBrokerCommission
from qstrader.exchange.csv_bar_data import CSVBarDataPriceVolumeDataSource
from qstrader.exchange.simulated_exchange import SimulatedExchange
from qstrader.simulation.daily_business_day_simulation_engine import (
    DailyBusinessDaySimulationEngine
)
from qstrader.simulation.trading_simulation import TradingSimulation


class BacktestTradingSimulation(TradingSimulation):
    """TODO: Fill in doc string!
    """

    def __init__(self, settings):
        self.settings = settings
        self.start_dt = self._create_start_date()
        self.end_dt = self._create_end_date()
        self.exchange_open_time_utc = self._create_exchange_open_time_utc()
        self.exchange_close_time_utc = self._create_exchange_close_time_utc()
        self.assets = self._create_assets()
        self.exchange = self._create_exchange()
        self.broker_commission = self._create_broker_commission()
        self.broker = self._create_broker()
        self.alpha_models = self._create_alpha_models()
        self.pcm = self._create_portfolio_construction()
        self.qta = self._create_quant_trading_algo()
        self.sim_engine = self._create_simulation_engine()

    def _create_start_date(self):
        """
        TODO: Fill in doc string!
        """
        return pd.Timestamp(
            self.settings.SIMULATION['START_DATE'], tz=pytz.UTC
        )

    def _create_end_date(self):
        """
        TODO: Fill in doc string!
        """
        return pd.Timestamp(
            self.settings.SIMULATION['END_DATE'], tz=pytz.UTC
        )

    def _create_exchange_open_time_utc(self):
        """
        TODO: Fill in doc string!
        """
        return pd.Timestamp(
            self.settings.EXCHANGE['OPENING_UTC'],
            tz=pytz.timezone(self.settings.EXCHANGE['TIMEZONE'])
        ).tz_convert("UTC")

    def _create_exchange_close_time_utc(self):
        """
        TODO: Fill in doc string!
        """
        return pd.Timestamp(
            self.settings.EXCHANGE['CLOSING_UTC'],
            tz=pytz.timezone(self.settings.EXCHANGE['TIMEZONE'])
        ).tz_convert("UTC")

    def _create_assets(self):
        """
        TODO: Fill in doc string!
        """
        tickers = self.settings.DATA['ASSETS']
        assets = [
            Equity(ticker, ticker, None, tax_exempt=True)
            for ticker in tickers
        ]
        return assets

    def _create_exchange(self):
        """
        TODO: Fill in doc string!
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
        TODO: Fill in doc string!
        """
        if self.settings.BROKER['COMMISSION']['MODEL'] == "Zero Commission":
            broker_commission = ZeroBrokerCommission()
        else:
            print(
                "No supported Broker Commission "
                "model specified. Exiting."
            )
            sys.exit()
        return broker_commission

    def _create_broker(self):
        """
        TODO: Fill in doc string!
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
        TODO: Fill in doc string!
        """
        if self.settings.SIMULATION['ALPHA']['MODEL'] == "Fixed Weight":
            alpha_model = FixedWeightAlphaModel
        else:
            print("No support Alpha Model model specified. Exiting.")
        alpha_models = [
            alpha_model(
                asset, self.start_dt,
                self.settings.SIMULATION['ALPHA']['WEIGHTS']
            ) for asset in self.assets
        ]
        return alpha_models

    def _create_portfolio_construction(self):
        """
        TODO: Fill in doc string!
        """
        pcm = FixedWeightPCM(
            self.start_dt, self.broker, self.portfolio_id,
            transaction_cost_model=self.broker_commission
        )
        return pcm

    def _create_quant_trading_algo(self):
        """
        TODO: Fill in doc string!
        """
        qta = QuantitativeTradingAlgorithm(
            self.start_dt, self.broker, self.portfolio_id,
            self.alpha_models, self.pcm
        )
        return qta

    def _create_simulation_engine(self):
        """
        TODO: Fill in doc string!
        """
        sim_engine = DailyBusinessDaySimulationEngine(
            self.start_dt, self.end_dt
        )
        return sim_engine

    def output_holdings(self):
        """
        TODO: Fill in doc string!
        """
        self.broker.portfolios[self.portfolio_id].holdings_to_console()

    def run(self):
        trading_events = ("market_open", "market_bar", "market_close")

        # Output a basic equity curve into the statistics directory
        perf = open(
            os.path.join(
                os.getcwd(),
                self.settings.STATISTICS_ROOT,
                'equity.csv'
            ), "w"
        )

        # Loop over all events
        for event in self.sim_engine:
            dt = event.ts

            # Update the exchange and all market prices
            self.exchange.update(dt)

            # Update the brokerage to modify portfolios
            # and/or carry out new orders
            self.broker.update(dt)

            # Update the trading algo to generate new orders
            if event.event_type in trading_events:
                self.qta.update(dt)

            # Update performance every trading day
            if event.event_type == "post_market":
                ptmv = self.broker.get_account_total_market_value()['master']
                perf.write("%s,%0.2f\n" % (dt, ptmv))
        perf.close()
