# QSTrader for Advanced Algorithmic Trading

QSTrader is an open-source event-driven backtesting platform for use in the equities markets. The majority of strategies within the [Advanced Algorithmic Trading](https://www.quantstart.com/advanced-algorithmic-trading-ebook/) ebook utilise QSTrader as the backtesting framework.

The software is provided under a permissive open source "MIT" license (see below).

# Installation

QSTrader can either be installed on a full Python distribution such as Anaconda (https://www.anaconda.com/distribution) or in a Python 3 virtual environment. We recommend Anaconda since it simplifies the installation process significantly.

QSTrader works best in a Linux-based system (e.g. MacOS or Ubuntu) since it is predominantly a command-line interface (CLI) tool. It can also be installed on Windows, but requires [Git](https://git-scm.com/) in order to install the version required for Advanced Algorithmic Trading.

## Creating a Python 3 Virtual Environment on Ubuntu

This section is for those who are comfortable using the Linux command line, Python virtual environments and the ```virtualenv``` tool. If you do not have experience with these tools the best way to install QSTrader is with the freely available Anaconda distribution (see above). If you have a working Anaconda installation please skip this section.

The first task is to create a new directory to store a virtual environment. We have utilised ```~/venv/qstrader``` within this section. If you wish to change this directory then rename it in the following steps.

Firstly create the new directory:

```
mkdir -p ~/venv/qstrader
```

Then we utilise the ```virtualenv``` tool to create a new Python virtual environment in that directory:

```
virtualenv --no-site-packages -p python3 ~/venv/qstrader
```

Then we can activate the virtual environment by typing the following:

```
source ~/venv/qstrader/bin/activate
```

## Installing Git

QSTrader is not yet part of the Python package repository. It cannot be directly installed via the usual ```pip``` approach. Instead it can be installed directly from this Git repository.

In order to carry this out it will be necessary to install Git on your system. The installation instructions of Git for various operating systems can be found at the [Git documentation](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

For instance, installing Git on Ubuntu Linux can be achieved with the following command:

```sudo apt-get install git-core```

## Installing QSTrader

Now that an appropriate Python environment has been installed (either Anaconda or virtual environment) along with the Git version control system it is possible to install QSTrader using ```pip```.

At this point it is necessary to use pip to install QSTrader as a library and then manually install the requirements.

The following steps will take some time (5-10 minutes) as QSTrader relies on NumPy, SciPy, Pandas, Matplotlib as well as many other libraries and hence they will all need to compile:

```
pip install git+https://github.com/mhallsmoore/qstrader.git@advanced-algorithmic-trading
```

If you have installed QSTrader into a new virtual environment (as opposed to Anaconda) then you will need to install the usual set of Python scientific libraries.

The installation of these libraries can be skipped if you already have a working Anaconda installation since it provides up to date versions of Python scientific libraries.

The libraries can be installed via pip:

```
pip install numpy
pip install scipy
pip install matplotlib
pip install pandas
pip install seaborn
```

Irrespective of your installation environment (Anaconda or virtualenv) you will need to install the following extra libraries:

```
pip install click
pip install pyyaml
pip install munch
pip install enum34
pip install multipledispatch
```

To check that QSTrader has been installed correctly open up a Python terminal and import QSTrader via the following command:

```
>>> import qstrader
```

If there is no error message then the library has been successfully installed.

If you have any trouble with the above instructions please contact us at [support@quantstart.com](mailto:support@quantstart.com).

# Example Usage

Now that the library itself and requirements have been installed it is necessary to create the default directories for data utilised in the backtests as well as output from the simulations.

As an example it is possible to download the necessary data and example code to run a simple backtest of a Buy And Hold strategy on the S&P500 total return index.

First create the necessary directories:

```
mkdir -p ~/qstrader/examples ~/data ~/out
```

Then download some example SPY data:

```
cd ~/data
wget https://raw.githubusercontent.com/mhallsmoore/qstrader/master/data/SPY.csv
```

Then download the example Buy And Hold backtest script:

```
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

If you have any questions about the installation or example usage then please feel free to email [support@quantstart.com](mailto:support@quantstart.com).

# License Terms

Copyright (c) 2015-2020 QuantStart.com, QuarkGluon Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Trading Disclaimer

Trading equities on margin carries a high level of risk, and may not be suitable for all investors. Past performance is not indicative of future results. The high degree of leverage can work against you as well as for you. Before deciding to invest in equities you should carefully consider your investment objectives, level of experience, and risk appetite. The possibility exists that you could sustain a loss of some or all of your initial investment and therefore you should not invest money that you cannot afford to lose. You should be aware of all the risks associated with equities trading, and seek advice from an independent financial advisor if you have any doubts.
