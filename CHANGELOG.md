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
