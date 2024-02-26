# QSTrader

| Development   | Details       |
| ------------- | ------------- |
| Test Status   | [![Build Status](https://img.shields.io/travis/mhallsmoore/qstrader?label=TravisCI&style=flat-square)](https://travis-ci.org/mhallsmoore/qstrader) [![Coverage Status](https://img.shields.io/coveralls/github/mhallsmoore/qstrader?style=flat-square&label=Coverage)](https://coveralls.io/github/mhallsmoore/qstrader?branch=master) |
| Version Info  | [![PyPI](https://img.shields.io/pypi/v/qstrader?style=flat-square&label=PyPI&color=blue)](https://pypi.org/project/qstrader) [![PyPI Downloads](https://img.shields.io/pypi/dm/qstrader?style=flat-square&label=PyPI%20Downloads)](https://pypi.org/project/qstrader) |
| Compatibility | [![Python Version](https://img.shields.io/pypi/pyversions/qstrader?style=flat-square&label=Python%20Versions)](https://pypi.org/project/qstrader) |
| License       | ![GitHub](https://img.shields.io/github/license/mhallsmoore/qstrader?style=flat-square&label=License) |

QSTrader is a free Python-based open-source modular schedule-driven backtesting framework for long-short equities and ETF based systematic trading strategies.

QSTrader can be best described as a loosely-coupled collection of modules for carrying out end-to-end backtests with realistic trading mechanics.

The default modules provide useful functionality for certain types of systematic trading strategies and can be utilised without modification. However the intent of QSTrader is for the users to extend, inherit or fully replace each module in order to provide custom functionality for their own use case.

The software is currently under active development and is provided under a permissive "MIT" license.

# Previous Version and Advanced Algorithmic Trading

Please note that the previous version of QSTrader, which is utilised through the **Advanced Algorithmic Trading** ebook, can be found along with the appropriate installation instructions [here](https://github.com/mhallsmoore/qstrader/tree/advanced-algorithmic-trading).

It has recently been updated to support Python 3.9, 3.10, 3.11 and 3.12 with up to date package dependencies.

# Installation

Installation requires a Python3 environment. The simplest approach is to download a self-contained scientific Python distribution such as the [Anaconda Individual Edition](https://www.anaconda.com/products/individual#Downloads). You can then install QSTrader into an isolated [virtual environment](https://docs.python.org/3/tutorial/venv.html#virtual-environments-and-packages) using pip as shown below.

Any issues with installation should be reported to the development team as issues [here](https://github.com/mhallsmoore/qstrader/issues).

## conda

[conda](https://docs.conda.io/projects/conda/en/latest/) is a command-line tool that comes with the Anaconda distribution. It allows you to manage virtual environments as well as packages _using the same tool_.

The following command will create a brand new environment called `backtest`.

```
conda create -n backtest python
```
This will use the conda default Python version. At time of writing this was Python 3.12. QSTrader currently supports Python 3.9, 3.10, 3.11 and 3.12. Optionally you can specify a python version by substituting python==3.9 into the command as follows:

```
conda create -n backtest python==3.9
```

In order to start using QSTrader, you need to activate this new environment and install QSTrader using pip.

```
conda activate backtest
pip3 install qstrader
```

## pip

Alternatively, you can use [venv](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments) to handle the environment creation and [pip](https://docs.python.org/3/tutorial/venv.html#managing-packages-with-pip) to handle the package installation.

```
python -m venv backtest
source backtest/bin/activate  # Need to activate environment before installing package
pip3 install qstrader
```

# Full Documentation

Comprehensive documentation and beginner tutorials for QSTrader can be found on QuantStart.com at [https://www.quantstart.com/qstrader/](https://www.quantstart.com/qstrader/).

# Quickstart

The QSTrader repository provides some simple example strategies at [/examples](https://github.com/mhallsmoore/qstrader/tree/master/examples).

Within this quickstart section a classic 60/40 equities/bonds portfolio will be backtested with monthly rebalancing on the last day of the calendar month.

To get started download the [sixty_forty.py](https://github.com/mhallsmoore/qstrader/blob/master/examples/sixty_forty.py) file and place into the directory of your choice.

The 60/40 script makes use of OHLC 'daily bar' data from Yahoo Finance. In particular it requires the [SPY](https://finance.yahoo.com/quote/SPY/history?p=SPY) and [AGG](https://finance.yahoo.com/quote/AGG/history?p=AGG) ETFs data. Download the full history for each and save as CSV files in same directory as ``sixty_forty.py``.

Assuming that an appropriate Python environment exists and QSTrader has been installed (see **Installation** above), make sure to activate the virtual environment, navigate to the directory with ``sixty_forty.py`` and type:

```
python sixty_forty.py
```

You will then see some console output as the backtest simulation engine runs through each day and carries out the rebalancing logic once per month. Once the backtest is complete a tearsheet will appear:

![Image of 60/40 Backtest](https://quantstartmedia.s3.amazonaws.com/images/qstrader_sixty_forty_backtest.png)

You can examine the commented ``sixty_forty.py`` file to see the current QSTrader backtesting API.

If you have any questions about the installation or example usage then please feel free to email [support@quantstart.com](mailto:support@quantstart.com) or raise an issue [here](https://github.com/mhallsmoore/qstrader/issues).

# Current Features

* **Backtesting Engine** - QSTrader employs a schedule-based portfolio construction approach to systematic trading. Signal generation is decoupled from portfolio construction, risk management, execution and simulated brokerage accounting in a modular, object-oriented fashion.

* **Performance Statistics** - QSTrader provides typical 'tearsheet' performance assessment of strategies. It also supports statistics export via JSON to allow external software to consume metrics from backtests.

* **Free Open-Source Software** - QSTrader has been released under a permissive open-source MIT License. This allows full usage in both research and commercial applications, without restriction, but with no warranty of any kind whatsoever (see **License** below). QSTrader is completely free and costs nothing to download or use.

* **Software Development** - QSTrader is written in the Python programming language for straightforward cross-platform support. QSTrader contains a suite of unit and integration tests for the majority of its modules. Tests are continually added for new features.

# License Terms

Copyright (c) 2015-2024 QuantStart.com, QuarkGluon Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Trading Disclaimer

Trading equities on margin carries a high level of risk, and may not be suitable for all investors. Past performance is not indicative of future results. The high degree of leverage can work against you as well as for you. Before deciding to invest in equities you should carefully consider your investment objectives, level of experience, and risk appetite. The possibility exists that you could sustain a loss of some or all of your initial investment and therefore you should not invest money that you cannot afford to lose. You should be aware of all the risks associated with equities trading, and seek advice from an independent financial advisor if you have any doubts.
