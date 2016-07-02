from abc import ABCMeta, abstractmethod

import datetime
import os
import csv


class Compliance(object):
    """
    The Compliance component should be given every trade
    that occurs in qstrader.

    It is designed to keep track of anything that may
    be required for regulatory or audit (or debugging)
    purposes. Extended versions can write trades to a
    CSV, or a database.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def record_trade(self, fill):
        """
        Takes a FillEvent from an ExecutionHandler
        and logs each of these.

        Parameters:
        fill - A FillEvent with information about the
        trade that has just been executed.
        """
        raise NotImplementedError("Should implement record_trade()")


class TestCompliance(Compliance):
    """
    A basic compliance module which writes trades to a
    CSV file in the output directory.
    """

    def __init__(self, config):
        """
        Wipe the existing trade log for the day, leaving only
        the headers in an empty CSV.

        It allows for multiple backtests to be run
        in a simple way, but quite likely makes it unsuitable for
        a production environment that requires strict record-keeping.
        """
        self.config = config
        # Remove the previous CSV file
        today = datetime.datetime.utcnow().date()
        self.csv_filename = "tradelog_" + datetime.datetime.today().strftime("%Y-%m-%d") + ".csv"
        self.csv_filename = "tradelog_" + today.strftime("%Y-%m-%d") + ".csv"

        try:
            os.remove(os.path.join(config.OUTPUT_DIR, self.csv_filename))
        except (IOError, OSError):
            print("No tradelog files to clean.")

        # Write new file header
        fieldnames = [
            "timestamp", "ticker",
            "action", "quantity",
            "exchange", "price",
            "commission"
        ]
        with open(os.path.join(self.config.OUTPUT_DIR, self.csv_filename), 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    def record_trade(self, fill):
        """
        Append all details about the FillEvent to the CSV trade log.
        """
        with open(os.path.join(self.config.OUTPUT_DIR, self.csv_filename), 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                fill.timestamp, fill.ticker,
                fill.action, fill.quantity,
                fill.exchange, fill.price,
                fill.commission
            ])
