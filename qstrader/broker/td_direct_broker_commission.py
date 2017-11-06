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

import pandas as pd

from qstrader.broker.broker_commission import BrokerCommission


class TDDirectBrokerCommission(BrokerCommission):
    """Handles the specific commission model provided
    by the TD Direct UK brokerage firm for UK equities.

    This was written as of 2017/10/02. It assumes these
    charges are active for the life-time of the backtest.
    That is, it does not take into account historic
    commission changes.

    The details can be found here:
    https://www.tddirectinvesting.co.uk/rates-and-charges

    If the trade value is below £100,000 then for the first
    three months there is an introductory rate. After three
    months, for £100,000 there are four separate rates:
    Active, Frequent, Standard and Regular Investment.

    Introductory: £3.95
    Active: Avg 20 or more eligible trades across last 3
        consecutive months: £5.95
    Frequent: Avg 10 or more eligible trades across last 3
        consecutive months: £8.95
    Standard: Avg of less than 10 trades per month across
        last 3 consecutive months: £12.50
    Regular Investment: To buy FTSE350 shares or ETFs by
        monthly Regular Investing facility.

    For transactions £100,000 to £500,000:
    Active, Frequent or Standard rate + £30.00

    For transactions >£500,000:
    Active, Frequent or Standard rate + £60.00

    Stamp Duty is 0.5% per trade of the consideration size, except
    for certain exempt shares.
    """
    def __init__(self):
        """
        Initialise the commission model.
        """
        self.rates = self._define_rates()

    def _define_rates(self):
        """
        Create the frequency of trading rates for commission calculation.

        The details can be found here:
        https://www.tddirectinvesting.co.uk/rates-and-charges/share-dealing
        """
        return {
            "introductory": 3.95,
            "active": 5.95,
            "frequent": 8.95,
            "standard": 12.50,
            "regular": 1.50
        }

    def _calc_commission(self, asset, consideration, broker=None):
        """
        Calculate the commission based on the rules in the
        class doc string.
        """
        commission = 0.0
        if consideration < 0.0:
            raise CommissionModelException(
                'Trade size of £%0.2f is negative. Cannot calculate '
                'commission for negative trade sizes.'
            )

        # Calculate activity and appropriate rate
        if broker is None:
            rate = "standard"
        else:
            if (
                hasattr(broker, "account_age") and 
                broker.account_age <= pd.Timedelta(days=90)
            ):
                rate = "introductory"
            else:
                if hasattr(broker, "num_trades_in_prev_days"):
                    num_trades = broker.num_trades_in_prev_days(90)
                    if num_trades >= 20:
                        rate = "active"
                    elif num_trades >= 10 and num_trades < 20:
                        rate = "frequent"
                    else:
                        rate = "standard"
                else:
                    rate = "standard"
        commission += self.rates[rate]

        # Make adjustment for trade size
        if consideration >= 100000.0 and consideration <= 500000.0:
            commission += 30.0
        if consideration > 500000.0:
            commission += 60.0
        return round(commission, 2)

    def _calc_tax(self, asset, consideration, broker=None):
        """
        Calculate the stamp duty tax, which is currently
        0.5% of the trade consideration.

        Certain shares are exempt from stamp duty so they
        must be checked first.
        """
        if consideration < 0.0:
            raise CommissionModelException(
                'Trade size of £%0.2f is negative. Cannot calculate '
                'stamp duty for negative trade sizes.'
            )
        # Check if share is exempt from stamp duty
        if asset.tax_exempt:
            return 0.0
        else:
            sdtax = 0.005 * consideration
            return round(sdtax, 2)

    def calc_total_cost(self, asset, consideration, broker=None):
        """
        Calculate the total of any commission and/or tax
        for the trade of size 'consideration'.
        """
        if consideration < 0.0:
            raise CommissionModelException(
                'Trade size of £%0.2f is negative. Cannot calculate '
                'total cost for negative trade sizes.'
            )
        commission = self._calc_commission(
            asset, consideration, broker=broker
        )
        tax = self._calc_tax(
            asset, consideration, broker=broker
        )
        return commission + tax
