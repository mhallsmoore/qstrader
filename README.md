[![Build Status](https://travis-ci.org/mhallsmoore/qstrader.svg?branch=master)](https://travis-ci.org/mhallsmoore/qstrader)
[![Coverage Status](https://coveralls.io/repos/github/mhallsmoore/qstrader/badge.svg?branch=master)](https://coveralls.io/github/mhallsmoore/qstrader?branch=master)

# Development News (6th November 2017)

We are pleased to announce that the QuantStart software development team are currently in the process of a complete redevelopment of QSTrader.

The new version will be an end-to-end quantitative trading simulation and live trading engine, rather than the current version which is limited to event-driven backtesting.

Significant progress has been made internally over the last couple of months. Some of this development has been made available on the ```develop``` branch, which can be found [here](https://github.com/mhallsmoore/qstrader/tree/develop).

The code will remain MIT licensed and every public release will require 100% code coverage.

If you wish to read more about the proposed developments please consult the [recent article](https://www.quantstart.com/articles/qstrader-a-major-update-on-our-progress) published on QuantStart.com.

# QSTrader  

QSTrader is an open-source event-driven backtesting platform for use in the equities markets, currently in an alpha state.

It has been created as part of the Advanced Trading Infrastructure article series on QuantStart.com to provide the systematic trading community with a robust trading engine that allows straightforward equities strategy implementation and testing.

The software is provided under a permissive "MIT" license (see below).

# Current Features

* **Open-Source** - QSTrader has been released under an extremely permissive open-source MIT License, which allows full usage in both research and commercial applications, without restriction, but with no warranty of any kind whatsoever. Thus you can use it at home to carry out retail trading or within a quant fund as a basis for your research and/or order management system.

* **Free** - QSTrader is completely free and costs nothing to download or use.

* **Collaboration** - As QSTrader is open-source many developers collaborate to improve the software. New features are added frequently. Any bugs are quickly determined and fixed.

* **Software Development** - QSTrader is written in the Python programming language for straightforward cross-platform support. QSTrader contains a suite of unit tests for the majority of its calculation code and tests are constantly added for new features.

* **Event-Driven Architecture** - QSTrader is completely event-driven, which leads to straightforward transitioning of strategies from a research phase to a live trading implementation.

* **Backtesting** - QSTrader supports both intraday tick-resolution (top of order book bid/ask) datasets as well as OHLCV "bar" resolution data on various time scales.

* **Private Components** - QSTrader allows you to include a repository of your own private strategies or components. Simply checkout your own repository within the root of QSTrader and rename the directory to `private_files`. This will ensure the QSTrader repository can be easily kept up to date without interfering with your private repository.

* **Performance Metrics** - QSTrader supports both portfolio-level and trade-level performance measurement. It provides a comprehensive "tearsheet" (see below) with associated strategy statistics.

# Planned Features

* **Transaction Costs** - Commissions are currently supported using Interactive Brokers standard fees for North American equities. Slippage and market impact are planned, but are not currently supported.

* **Trading** - QSTrader will support live intraday trading using the Interactive Brokers native Python API, initially for North American equities.

# Installation and Example Usage

QSTrader is in an early alpha state at the moment. It should only be used for exploratory backtesting research. The installation procedure is a little more involved than a standard Python package as it has not yet been added to the Python package repository.

Ubuntu Linux is the recommended platform on which to install QSTrader, but it will also work on Windows or Mac OSX under the Anaconda distribution (https://www.continuum.io/downloads).

For those that wish to create their own Python virtual environment the following steps are necessary to run both a basic Buy And Hold strategy as well as a slightly more complex Moving Average Crossover trend-following strategy.

An example virtual environment directory ```~/venv/qstraderp3``` has been used here. If you wish to change this directory then rename it in the following steps.

The following steps will create a virtual environment directory with Python 3 and then activate the environment:

```
mkdir -p ~/venv/qstraderp3
cd ~/venv/qstraderp3
virtualenv --no-site-packages -p python3 .
source ~/venv/qstraderp3/bin/activate
```

At this point it is necessary to use pip to install QSTrader as a library and then manually install the requirements. The following steps will take some time (5-10 minutes) as QSTrader relies on NumPy, SciPy, Pandas, Matplotlib as well as many other libraries and hence they will all need to compile:

```
pip install git+https://github.com/mhallsmoore/qstrader.git
pip install -r https://raw.githubusercontent.com/mhallsmoore/qstrader/master/requirements.txt
```

Now that the library itself and requirements have been installed it is necessary to create the default directories for the data and output. In addition it is possible to download the necessary data and example code to run a simple backtest of a Buy And Hold strategy on the S&P500 total return index:

```
mkdir -p ~/qstrader/examples ~/data ~/out
cd ~/data
wget https://raw.githubusercontent.com/mhallsmoore/qstrader/master/data/SPY.csv
cd ~/qstrader/examples
wget https://raw.githubusercontent.com/mhallsmoore/qstrader/master/examples/buy_and_hold_backtest.py 
```

Finally, we can run the backtest itself: 

```
python buy_and_hold_backtest.py
```

Once complete you will see a full "tearsheet" of results including:

* Equity curve
* Drawdown curve
* Monthly returns heatmap
* Yearly returns distribution
* Portfolio-level statistics
* Trade-level statistics

The tearsheet will look similar to:

![alt tag](https://s3.amazonaws.com/quantstart/media/images/qstrader-buy-and-hold-tearsheet.png)

You can explore the ```buy_and_hold_backtest.py``` file to examine the API of QSTrader. You will see that it is relatively straightforward to set up a simple strategy and execute it.

For slightly more complex buy and sell rules it is possible to consider a Moving Average Crossover strategy. 

The following strategy creates two Simple Moving Averages with respective lookback periods of 100 and 300 days. When the 100-period SMA exceeds the 300-period SMA 100 shares of AAPL are longed. When the 300-period SMA exceeds the 100-period SMA the position is closed out. To obtain the data for this strategy and execute it run the following code:

```
cd ~/data
wget https://raw.githubusercontent.com/mhallsmoore/qstrader/master/data/AAPL.csv
cd ~/qstrader/examples
wget https://raw.githubusercontent.com/mhallsmoore/qstrader/master/examples/moving_average_cross_backtest.py 
```

The backtest can be executed with the following command:

```
python moving_average_cross_backtest.py
```

Once complete a full tearsheet will be presented, this time with a benchmark:

![alt tag](https://s3.amazonaws.com/quantstart/media/images/qstrader-moving-average-cross-tearsheet.png)

Other example strategies can be found in the ```examples``` directory. Each example is self-contained in a ```****_backtest.py``` file, which can be used as templates for your own strategies.

The project is constantly being developed, so unfortunately it is likely that the current API will experience backwards incompatibility until a mature beta version has been produced.

If you have any questions about the installation then please feel free to email support@quantstart.com.

If you notice any bugs or other issues that you think may be due to the codebase specifically, feel free to open a Github issue here: https://github.com/mhallsmoore/qstrader/issues

# License Terms

Copyright (c) 2015-2017 QuantStart.com, QuarkGluon Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Trading Disclaimer

Trading equities on margin carries a high level of risk, and may not be suitable for all investors. Past performance is not indicative of future results. The high degree of leverage can work against you as well as for you. Before deciding to invest in equities you should carefully consider your investment objectives, level of experience, and risk appetite. The possibility exists that you could sustain a loss of some or all of your initial investment and therefore you should not invest money that you cannot afford to lose. You should be aware of all the risks associated with equities trading, and seek advice from an independent financial advisor if you have any doubts.
