# 0.2.5

* Moved build-backend system to Hatchling from setuptools
* Updated the python package requirements to work with click 8.1
* Updated ReadMe and ChangeLog.

# 0.2.4

* Fixed bug involving NaN at Timestamp in sixty_forty example.
* Removed support for python 3.7 and 3.8
* Updated the python package requirements to work with matplotlib 3.8, numpy 1.26 and pandas 2.2.0

# 0.2.3

* Updated the python package requirements to work with matplotlib 3.4, numpy 1.21 and pandas 1.3
* Removed support for python 3.6
* Added a Tactical Asset Allocation monthly momentum strategy to the examples

# 0.2.2

* Added link to full documentation at [https://www.quantstart.com/qstrader/](https://www.quantstart.com/qstrader/)
* Fixed bug where burn-in period was still allowing portfolio rebalances and trade executions
* Added QSTrader Dockerfiles for various Linux distributions
* Removed support for Python 3.5 and added support for Python 3.9
* Increased minimum supported Pandas version to 1.1.5 from 0.25.1
* Modified end-to-end backtest integration test to check for approximate equality of results to fix differences across Pandas versions
* Disallowed Matplotlib 3.3.3 temporarily to avoid deprecated functionality from causing errors
* Event print messages during backtests can now be disabled through a boolean setting

# 0.2.1

* Added VolatilitySignal class to calculate rolling annualised volatility of returns for an asset
* Removed errors for orders that exceed cash account balance in SimulatedBroker and Portfolio. Replaced with console warnings.

# 0.2.0

* Significant overhaul of Position, PositionHandler, Portfolio, Transaction and SimulatedBroker classes to correctly account for short selling of assets
* Addition of LongShortLeveragedOrderSizer to allow long/short leveraged portfolios
* Added a new long/short leveraged portfolio example backtest
* Added some unit and integration tests to improve test coverage slightly

# 0.1.4

* Added ValueError with more verbose description for NaN pricing data when backtest start date too early
* Removed usage of 'inspect' library for updating attributes of Position within PositionHandler
* Added unit tests for Cash asset, StaticUniverse, DynamicUniverse and string colour utility function
* Added two more statistics to the JSON statistics calculation

# 0.1.3

* Fixed bug involving DynamicUniverse not adding assets to momentum and signal calculation if not present at start of backtest
* Modified MomentumSignal and SMASignal to allow calculation if available prices less than lookbacks
* Added daily rebalancing capability
* Added some unit tests to improve test coverage slightly

# 0.1.2

* Added RiskModel class hierarchy
* Modified API for MomentumSignal and SMASignal to utilise inherited Signal object
* Added SignalsCollection entity to update data for derived Signal classes
* Removed unnecessary BufferAlphaModel
* Added some unit tests to improve test coverage slightly

# 0.1.1

* Removed the need to specify a CSV data directory as an environment variable by adding a default of the current working directory of the executed script
* Addes CI support for Python 3.5, 3.6 and 3.8 in addition to 3.7
* Added some unit tests to improve test coverage slightly

# 0.1.0

* Initial relase of QSTrader to PyPI
