from __future__ import print_function

import calendar
import copy
import datetime
import os
import sys

import numpy as np


def month_weekdays(year_int, month_int):
    """
    Produces a list of datetime.date objects representing the
    weekdays in a particular month, given a year.
    """
    cal = calendar.Calendar()
    return [
        d for d in cal.itermonthdates(year_int, month_int)
        if d.weekday() < 5 and d.year == year_int
    ]


if __name__ == "__main__":
    try:
        fixtures_dir = sys.argv[1]
        ticker = sys.argv[2]
        init_price = sys.argv[3]
        random_seed = sys.argv[4]
    except IndexError:
        print(
            "You need to enter an equity ticker symbol and a "
            "fixtures directory as command line parameters."
        )
    else:
        np.random.seed(int(random_seed))  # Fix the randomness

        S0 = float(init_price)
        spread = 0.02
        mu_dt = 1400  # Milliseconds
        sigma_dt = 100  # Millseconds
        ask = copy.deepcopy(S0) + spread / 2.0
        bid = copy.deepcopy(S0) - spread / 2.0
        days = month_weekdays(2016, 2)[:1]  # January 2014
        current_time = datetime.datetime(
            days[0].year, days[0].month, days[0].day, 0, 0, 0,
        )

        # Loop over every day in the month and create a CSV file
        # for each day, e.g. "GOOG_20150101.csv"
        for d in days:
            print(d.day)
            current_time = current_time.replace(day=d.day)
            outfile = open(
                os.path.join(
                    fixtures_dir,
                    "%s.csv" % ticker
                ), "w")
            outfile.write("Ticker,Time,Bid,Ask\n")

            # Create the random walk for the bid/ask prices
            # with fixed spread between them
            # while True:
            for i in range(0, 10000):
                dt = abs(np.random.normal(mu_dt, sigma_dt))
                current_time += datetime.timedelta(0, 0, 0, dt)
                if current_time.day != d.day:
                    outfile.close()
                    break
                else:
                    W = np.random.standard_normal() * dt / 1000.0 / 86400.0
                    ask += W
                    bid -= W
                    line = "%s,%s,%s,%s\n" % (
                        ticker,
                        current_time.strftime(
                            "%d.%m.%Y %H:%M:%S.%f"
                        )[:-3],
                        "%0.5f" % bid,
                        "%0.5f" % ask
                    )
                    outfile.write(line)
