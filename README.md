![GitHub](https://img.shields.io/github/license/mhallsmoore/qstrader)
[![Build Status](https://travis-ci.org/mhallsmoore/qstrader.svg?branch=master)](https://travis-ci.org/mhallsmoore/qstrader)
[![Coverage Status](https://coveralls.io/repos/github/mhallsmoore/qstrader/badge.svg?branch=development)](https://coveralls.io/github/mhallsmoore/qstrader?branch=master)
[![Python Version](https://img.shields.io/pypi/pyversions/qstrader)](https://pypi.org/project/qstrader)

# QSTrader

QSTrader is a free Python-based open-source modular schedule-driven backtesting framework for long-only equities and ETF based systematic trading strategies.

QSTrader can be best described as a loosely-coupled collection of modules for carrying out end-to-end backtests with realistic trading mechanics. 

The default modules provide useful functionality for certain types of systematic trading strategies and can be utilised without modification. However the intent of QSTrader is for the users to extend, inherit or fully replace each module in order to provide custom functionality for their own use case.

The software is currently under active development (semantic version 0.x.x) and is provided under a permissive "MIT" license.

# Previous Version and Advanced Algorithmic Trading

Please note that the previous version of QSTrader, which is utilised through the **Advanced Algorithmic Trading** ebook, can be found along with the appropriate installation instructions [here](https://github.com/mhallsmoore/qstrader/tree/advanced-algorithmic-trading).

It has recently been updated to support Python 3.5, 3.6 and 3.7 with up to date package dependencies.

# Installation

Installation requires a Python3 environment. The simplest approach is to download a self-contained scientific Python distribution such as the [Anaconda Individual Edition](https://www.anaconda.com/products/individual#Downloads). Then you can install QSTrader via pip:

```
pip install qstrader
```

Any issues with installation should be reported to the development team as issues [here](https://github.com/mhallsmoore/qstrader/issues).

# Current Features

* **Backtesting Engine** - QSTrader employs a schedule-based portfolio construction approach to systematic trading. Signal generation is decoupled from portfolio construction, risk management, execution and simulated brokerage accounting in a modular, object-oriented fashion.

* **Performance Statistics** - QSTrader provides typical 'tearsheet' performance assessment of strategies. It also supports statistics export via JSON to allow external software to consume metrics from backtests.

* **Free Open-Source Software** - QSTrader has been released under a permissive open-source MIT License. This allows full usage in both research and commercial applications, without restriction, but with no warranty of any kind whatsoever (see **License** below). QSTrader is completely free and costs nothing to download or use.

* **Software Development** - QSTrader is written in the Python programming language for straightforward cross-platform support. QSTrader contains a suite of unit and integration tests for the majority of its modules. Tests are continually added for new features.

# License Terms

Copyright (c) 2015-2020 QuantStart.com, QuarkGluon Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Trading Disclaimer

Trading equities on margin carries a high level of risk, and may not be suitable for all investors. Past performance is not indicative of future results. The high degree of leverage can work against you as well as for you. Before deciding to invest in equities you should carefully consider your investment objectives, level of experience, and risk appetite. The possibility exists that you could sustain a loss of some or all of your initial investment and therefore you should not invest money that you cannot afford to lose. You should be aware of all the risks associated with equities trading, and seek advice from an independent financial advisor if you have any doubts.
