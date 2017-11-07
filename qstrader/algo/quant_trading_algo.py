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


class QuantitativeTradingAlgorithm(object):
    """TODO: Add docstring!
    """

    def __init__(
        self, start_dt,
        broker, broker_portfolio_id,
        alpha_models, pcm
    ):
        self.start_dt = start_dt
        self.broker = broker
        self.broker_portfolio_id = broker_portfolio_id
        self.alpha_models = alpha_models
        self.pcm = pcm

    def update(self, dt):
        # Create the list of forecasts from AlphaModels
        forecasts = []
        for alpha in self.alpha_models:
            alpha.update(dt)
            forecast = alpha.forecast()
            forecasts.append(forecast)

        # Generate the list of orders
        self.pcm.update(dt)
        order_list = self.pcm.generate_orders(forecasts)

        # Send the orders to the broker
        for order in order_list:
            self.broker.submit_order(self.broker_portfolio_id, order)
