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


class ForecastException(Exception):
    pass


class Forecast(object):
    """Encapsulates the concept of forecasting an asset
    direction or magnitude over a certain time window.

    A list of Forecast instances is provided to the
    PortfolioConstructionModel to ultimately create
    potential Order entities to be executed.

    Paramaters
    ----------
    asset : Asset
        The Asset instance on which to provide a forecast.
    value : float
        The floating point value of the forecast. Such a
        value is specific to the user. Typical examples 
        might include +1, 0, -1 for trend following, 
        -10 to +10 for 'strength' of forecasts or a
        ranking system 1,...,N for momentum stock ranking.
    created_dt : pd.Timestamp
        The UTC time that the forecast was generated.
    forecast_dt : pd.Timestamp
        The UTC time that the forecast is for.
    """

    def __init__(
        self, asset, value, 
        created_dt, forecast_dt
    ):
        """
        Initialise the forecast instance.
        """
        self.asset = asset
        self.value = value
        self.created_dt = created_dt
        self.forecast_dt = forecast_dt
        if self.forecast_dt < self.created_dt:
            raise ForecastException(
                "Cannot create a forecast for time %s, "
                "which is before the created time of %s." % (
                    self.forecast_dt, self.created_dt
                )
            )

    def forecast_duration(self):
        """
        Produce a timedelta for the forecast duration.
        """
        return self.forecast_dt - self.created_dt
