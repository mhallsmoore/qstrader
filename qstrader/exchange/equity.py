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

from qstrader.exchange.asset import Asset


class Equity(Asset):
    """Stores meta data about an equity stock or "share".

    Data includes its name, exchange, ticker symbol as 
    well as a reference to its trading exchange.

    Parameters
    ----------
    name : str
        The asset's name (e.g. the company name and/or 
        share class).
    symbol : str
        The asset's original ticker symbol.
        TODO: This requires modification to handle proper
        ticker mapping.
    exchange : Exchange
        A reference to the Exchange that the asset is
        trading on.
    tax_exempt: boolean
        Is the share exempt from government taxation? 
        Necessary for taxation on share transactions, such
        as UK stamp duty.
    """

    def __init__(
        self, name, symbol, 
        exchange, tax_exempt=False
    ):
        self.name = name
        self.symbol = symbol
        self.exchange = exchange
        self.tax_exempt = tax_exempt

    @classmethod
    def from_dict(cls, asset_dict):
        """
        Build an Equity Asset from the provided dictionary.
        """
        return cls(**asset_dict)

    def to_dict(self):
        """
        Represent the Equity Asset as a dictionary.
        """
        return {
            "name": self.name,
            "symbol": self.symbol,
            "exchange": self.exchange,
            "tax_exempt": self.tax_exempt
        }
