[![Build Status](https://travis-ci.org/mhallsmoore/qstrader.svg?branch=master)](https://travis-ci.org/mhallsmoore/qstrader)
[![Coverage Status](https://coveralls.io/repos/github/mhallsmoore/qstrader/badge.svg?branch=master)](https://coveralls.io/github/mhallsmoore/qstrader?branch=master)

# QSTrader  

QSTrader is an open-source event-driven backtesting and live trading platform for use in the equities markets, currently in an early "alpha" state.

It has been created as part of the Advanced Trading Infrastructure article series on QuantStart.com to provide the systematic trading community with a robust trading engine that allows straightforward equities/ETF strategy implementation and testing.

The software is provided under a permissive "MIT" license (see below).

# Current Features

* **Open-Source** - QSTrader has been released under an extremely permissive open-source MIT License, which allows full usage in both research and commercial applications, without restriction, but with no warranty of any kind whatsoever. Thus you can use it at home to carry out retail trading or within a quant fund as a basis for your research and/or order management system.

* **Free** - QSTrader is completely free and costs nothing to download or use.

* **Collaboration** - As QSTrader is open-source many developers collaborate to improve the software. New features are added frequently. Any bugs are quickly determined and fixed.

* **Software Development** - QSTrader is written in the Python programming language for straightforward cross-platform support. QSTrader contains a suite of unit tests for the majority of its calculation code and tests are constantly added for new features.

* **Event-Driven Architecture** - QSTrader is completely event-driven both for backtesting and live trading, which leads to straightforward transitioning of strategies from a research/testing phase to a live trading implementation.

* **Backtesting** - QSTrader supports both intraday tick-resolution (top of order book bid/ask) datasets as well as OHLCV "bar" resolution data on various time scales.

* **Private Components** - QSTrader allows you to include a repository of your own private strategies or components. Simply checkout your own repository within the root of QSTrader and rename the directory to `private_files`. This will ensure the QSTrader repository can be easily kept up to date without interfering with your private repository.

* **Performance Metrics** - QSTrader will supports basic strategy/portfolio performance measurement and equity curve visualisation via the Matplotlib and Seaborn visualisation libraries.

# Planned Features

* **Transaction Costs** - Fees/commission, slippage and market impact will all be simulated using realistic assumptions. This means the costs predicted in backtests will be similar to those encountered in live trading.

* **Trading** - QSTrader will support live intraday trading using the Interactive Brokers API across a set of equities/ETFs.

# Installation and Example Usage

QSTrader is in an extremely early alpha state at the moment and should only be used for exploratory backtesting research. The installation procedure is a little more involved than a standard Python package as it has not been added to the Python package repository yet.

Ubuntu is the recommended platform on which to install QSTrader, but it will also work on Windows or Mac OSX under the Anaconda distribution (https://www.continuum.io/downloads).

For those that wish to create their own virtual environment, the following steps are necessary to run a basic Buy And Hold strategy.

An example virtual environment directory ```~/venv/qstraderp3``` has been used for this example. If you wish to change this directory then re-name it in the following steps.

The following steps will create a virtual environment directory with Python 3 and then activate the environment:

```
mkdir -p ~/venv/qstraderp3
cd ~/venv/qstraderp3
virtualenv --no-site-packages -p /usr/bin/python3 .
source ~/venv/qstraderp3/bin/activate
```

At this point it is necessary to use pip to install QSTrader as a library and then manually install the requirements. The following steps will take some time as QSTrader relies on NumPy, SciPy, Pandas, Matplotlib as well as many other libraries and hence they will all need to compile:

```
pip install git+https://github.com/mhallsmoore/qstrader.git
pip install -r https://raw.githubusercontent.com/mhallsmoore/qstrader/master/requirements.txt
```

Now that the library itself and requirements have been installed it is necessary to create the default directories for the data and output. In addition it is possible to download the necessary data and example code to run a simple backtest of a Buy And Hold strategy on the S&P500 total return index:

```
mkdir -p ~/qstrader/examples ~/data ~/out
cd ~/data
wget https://raw.githubusercontent.com/mhallsmoore/qstrader/master/data/SP500TR.csv
cd ~/qstrader/examples
wget https://raw.githubusercontent.com/mhallsmoore/qstrader/master/examples/buy_and_hold_backtest.py 
```

Finally, we can run the backtest itself: 

```
python buy_and_hold_backtest.py
```

Once complete you will see performance charts indicating:

* Equity curve
* Period returns
* Drawdown

The chart will look similar to:

![alt tag](https://s3.amazonaws.com/quantstart/media/images/qstrader-buy-and-hold.png)

The project is constantly being developed, so unfortunately it is likely that the current API will experience backwards incompatibility until a mature beta version has been produced.

If you have any questions about the installation then please feel free to email support@quantstart.com.

If you notice any bugs or other issues that you think may be due to the codebase specifically, feel free to open a Github issue here: https://github.com/mhallsmoore/qstrader/issues

# License Terms

Copyright (c) 2015-2016 Michael Halls-Moore

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Trading Disclaimer

Trading equities on margin carries a high level of risk, and may not be suitable for all investors. Past performance is not indicative of future results. The high degree of leverage can work against you as well as for you. Before deciding to invest in equities you should carefully consider your investment objectives, level of experience, and risk appetite. The possibility exists that you could sustain a loss of some or all of your initial investment and therefore you should not invest money that you cannot afford to lose. You should be aware of all the risks associated with equities trading, and seek advice from an independent financial advisor if you have any doubts.
