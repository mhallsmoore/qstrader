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

from qstrader.simulation.trading_simulation import TradingSimulation


class BacktestTradingSimulation(TradingSimulation):
    """TODO: Fill in doc string!
    """

    def __init__(
        self, sim_engine, trading_algo, exchange, broker
    ):
        self.sim_engine = sim_engine
        self.trading_algo = trading_algo
        self.exchange = exchange
        self.broker = broker

    def run(self):
        trading_events = ("market_open", "market_bar", "market_close")

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
                self.trading_algo.update(dt)

            # Update performance every trading day
            #if event.event_type == "post_market":
            #    performance.update(dt)
            # TODO: Add this in!

        # Summarise performance at end of backtest
        # TODO: Add this in!
