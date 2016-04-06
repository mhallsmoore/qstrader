# QSTrader

QSTrader is an open-source event-driven backtesting and live trading platform for use in the equities markets, currently in an early "alpha" state.

It has been created as part of the Advanced Trading Infrastructure article series on QuantStart.com to provide the systematic trading community with a robust trading engine that allows straightforward equities/ETF strategy implementation and testing. 

The software is provided under a permissive "MIT" license (see below).

# Current Features

* **Open-Source** - QSTrader has been released under an extremely permissive open-source MIT License, which allows full usage in both research and commercial applications, without restriction, but with no warranty of any kind whatsoever.

* **Free** - QSTrader is completely free and costs nothing to download or use.

* **Collaboration** - As QSTrader is open-source many developers collaborate to improve the software. New features are added frequently. Any bugs are quickly determined and fixed.

* **Software Development** - QSTrader is written in the Python programming language for straightforward cross-platform support. QSTrader contains a suite of unit tests for the majority of its calculation code and tests are constantly added for new features.

* **Event-Driven Architecture** - QSTrader is completely event-driven both for backtesting and live trading, which leads to straightforward transitioning of strategies from a research/testing phase to a live trading implementation.

* **Backtesting** - QSTrader supports intraday tick-resolution (top of order book bid/ask) datasets.

# Planned Features

* **Transaction Costs** - Fees/commission, slippage and market impact will all be simulated using realistic assumptions. This means the costs predicted in backtests will be similar to those encountered in live trading.

* **Trading** - QSTrader will support live intraday trading using the Interactive Brokers API across a set of equities/ETFs.

* **Performance Metrics** - QSTrader will support extensive strategy/portfolio performance measurement and equity curve visualisation via the Matplotlib and Seaborn visualisation libraries.

# Installation and Usage

QSTrader is in an extremely early alpha state at the moment and should only be used for exploratory backtesting research. 

In time this section will contain detailed installation instructions. At this point the best way to get started is to install an all-in-one platform-independent Python distribution such as Anaconda, that contains all of the necessary libraries, such as NumPy, SciPy, Pandas, Matplotlib and Seaborn.

Once installed you can clone the repository by typing the following command in your terminal: ```git clone https://github.com/mhallsmoore/qstrader.git```. Alternatively you can download the zip file of the current master branch at https://github.com/mhallsmoore/qstrader/archive/master.zip.

You will need to create a symbolic link to the qstrader application root (the directory that contains the LICENSE and the README.md) in your Python virtual environment, in order for ```import qstrader``` statements to function correctly. 

At this stage there is only one simple backtest example in ```examples/test_strategy_backtest.py```. This test itself requires some equities testing data. In the future the codebase will come with some sophisticated equity data simulators, so that any strategies can be tested without having to fetch external data, prior to a realistic test.

Future versions will also make use of a ```settings.py``` file to specify local input and output directories, as well as any authentication information required by a brokerage to authenticate against their API for live trading.

The project is constantly being developed, so unfortunately it is likely that the current API will experience backwards incompatibility until a mature beta version has been produced.

If you have any questions about the installation then please feel free to email feedback@quantstart.com.

If you notice any bugs or other issues that you think may be due to the codebase specifically, feel free to open a Github issue here: https://github.com/mhallsmoore/qstrader/issues

# License Terms

Copyright (c) 2016 Michael Halls-Moore

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Trading Disclaimer

Trading equities on margin carries a high level of risk, and may not be suitable for all investors. Past performance is not indicative of future results. The high degree of leverage can work against you as well as for you. Before deciding to invest in equities you should carefully consider your investment objectives, level of experience, and risk appetite. The possibility exists that you could sustain a loss of some or all of your initial investment and therefore you should not invest money that you cannot afford to lose. You should be aware of all the risks associated with equities trading, and seek advice from an independent financial advisor if you have any doubts.
