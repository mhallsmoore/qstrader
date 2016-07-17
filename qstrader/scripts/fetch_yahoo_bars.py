from __future__ import print_function

import click
import csv
import requests
import datetime
import os
import pandas as pd
from qstrader import settings

def run(config, tickers):
    """
    Script fetches all daily bars from Yahoo between 2000 and today, and
    formats correctly for immediate use with qstrader. Also allows user to
    specify a CSV file of tickers as input, to allow for >100 tickers to be
    downloaded easily.
    """
    start = (2000,1,1)
    end = datetime.date.today().timetuple()[0:3]
    failed_tickers = []
    successful_downloads = 0

    for ticker in tickers:
        # Prepare the URL query
        parameters = (
            ticker, start[1]-1, start[2], start[0],
            end[1]-1, end[2], end[0],
        )
        url = "http://ichart.finance.yahoo.com/table.csv"
        url += "?s=%s&a=%s&b=%s&c=%s&d=%s&e=%s&f=%s"
        url = url % parameters

        # Attempt to request the data
        try:
            data = requests.get(url).text.split("\n")[1:-1]
            output = []
            for row in data:
                pieces = row.strip().split(',')
                output.append(
                    (pieces[0], pieces[1], pieces[2], pieces[3],
                    pieces[4], pieces[5], pieces[6])
                )
        except Exception as e:
            print("Exeption trying to download: %s" % e)
            print("FAILED TICKER: " + ticker)
            failed_tickers.append(ticker)

        # Format into a DataFrame because qstrader uses them elsewhere
        df = pd.DataFrame(
            output,
            columns=("Date", "Open", "High", "Low","Close", "Volume", "Adj Close")
        )

        # Write output to CSV
        df.to_csv(config.CSV_DATA_DIR + "/" + ticker + ".csv", index = False)
        successful_downloads = successful_downloads + 1
        print("Written " + ticker + ".csv to data directory")

    print("Downloaded %s files successfully." % successful_downloads)
    print("Faied downloads: " + failed_tickers)



@click.command()
@click.option('--config', default=settings.DEFAULT_CONFIG_FILENAME, help='Config filename')
@click.option('--tickers', default='FB,AMZN,NFLX,GOOG', help='Equity ticker symbols, comma separated. Can take in a CSV file.')

def main(config, tickers):
    config = settings.from_file(config)

    if os.path.isfile(tickers):
        try:
            with open(tickers, 'r') as f:
                reader = csv.reader(f)
                tickers = list(reader)[0]
        except Exception:
            print("Could not load CSV file of ticker input correctly.")
            return

    else:
        tickers = tickers.split(",")
    return run(config, tickers)

if __name__ == "__main__":
    main()
