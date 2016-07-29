import unittest

from qstrader.price_parser import PriceParser
from qstrader.price_handler.historic_csv_tick import HistoricCSVTickPriceHandler
from qstrader.compat import queue
from qstrader import settings


class TestPriceHandlerSimpleCase(unittest.TestCase):
    """
    Test the initialisation of a PriceHandler object with
    a small list of tickers. Concatenate the ticker data (
    pre-generated and stored as a fixture) and stream the
    subsequent ticks, checking that the correct bid-ask
    values are returned.
    """
    def setUp(self):
        """
        Set up the PriceHandler object with a small
        set of initial tickers.
        """
        self.config = settings.TEST
        fixtures_path = self.config.CSV_DATA_DIR
        events_queue = queue.Queue()
        init_tickers = ["GOOG", "AMZN", "MSFT"]
        self.price_handler = HistoricCSVTickPriceHandler(
            fixtures_path, events_queue, init_tickers
        )

    def test_stream_all_ticks(self):
        """
        The initialisation of the class will open the three
        test CSV files, then merge and sort them. They will
        then be stored in a member "tick_stream". This will
        be used for streaming the ticks.
        """
        # Stream to Tick #1 (GOOG)
        self.price_handler.stream_next()
        self.assertEqual(
            self.price_handler.tickers["GOOG"]["timestamp"].strftime(
                "%d-%m-%Y %H:%M:%S.%f"
            ),
            "01-02-2016 00:00:01.358000"
        )
        self.assertEqual(
            PriceParser.display(self.price_handler.tickers["GOOG"]["bid"], 5),
            683.56000
        )
        self.assertEqual(
            PriceParser.display(self.price_handler.tickers["GOOG"]["ask"], 5),
            683.58000
        )

        # Stream to Tick #2 (AMZN)
        self.price_handler.stream_next()
        self.assertEqual(
            self.price_handler.tickers["AMZN"]["timestamp"].strftime(
                "%d-%m-%Y %H:%M:%S.%f"
            ),
            "01-02-2016 00:00:01.562000"
        )
        self.assertEqual(
            PriceParser.display(self.price_handler.tickers["AMZN"]["bid"], 5),
            502.10001
        )
        self.assertEqual(
            PriceParser.display(self.price_handler.tickers["AMZN"]["ask"], 5),
            502.11999
        )

        # Stream to Tick #3 (MSFT)
        self.price_handler.stream_next()
        self.assertEqual(
            self.price_handler.tickers["MSFT"]["timestamp"].strftime(
                "%d-%m-%Y %H:%M:%S.%f"
            ),
            "01-02-2016 00:00:01.578000"
        )
        self.assertEqual(
            PriceParser.display(self.price_handler.tickers["MSFT"]["bid"], 5),
            50.14999
        )
        self.assertEqual(
            PriceParser.display(self.price_handler.tickers["MSFT"]["ask"], 5),
            50.17001
        )

        # Stream to Tick #10 (GOOG)
        for i in range(4, 11):
            self.price_handler.stream_next()
        self.assertEqual(
            self.price_handler.tickers["GOOG"]["timestamp"].strftime(
                "%d-%m-%Y %H:%M:%S.%f"
            ),
            "01-02-2016 00:00:05.215000"
        )
        self.assertEqual(
            PriceParser.display(self.price_handler.tickers["GOOG"]["bid"], 5),
            683.56001
        )
        self.assertEqual(
            PriceParser.display(self.price_handler.tickers["GOOG"]["ask"], 5),
            683.57999
        )

        # Stream to Tick #20 (GOOG)
        for i in range(11, 21):
            self.price_handler.stream_next()
        self.assertEqual(
            self.price_handler.tickers["MSFT"]["timestamp"].strftime(
                "%d-%m-%Y %H:%M:%S.%f"
            ),
            "01-02-2016 00:00:09.904000"
        )
        self.assertEqual(
            PriceParser.display(self.price_handler.tickers["MSFT"]["bid"], 5),
            50.15000
        )
        self.assertEqual(
            PriceParser.display(self.price_handler.tickers["MSFT"]["ask"], 5),
            50.17000
        )

        # Stream to Tick #30 (final tick, AMZN)
        for i in range(21, 31):
            self.price_handler.stream_next()
        self.assertEqual(
            self.price_handler.tickers["AMZN"]["timestamp"].strftime(
                "%d-%m-%Y %H:%M:%S.%f"
            ),
            "01-02-2016 00:00:14.616000"
        )
        self.assertEqual(
            PriceParser.display(self.price_handler.tickers["AMZN"]["bid"], 5),
            502.10015
        )
        self.assertEqual(
            PriceParser.display(self.price_handler.tickers["AMZN"]["ask"], 5),
            502.11985
        )

    def test_subscribe_unsubscribe(self):
        """
        Tests the 'subscribe_ticker' and 'unsubscribe_ticker'
        methods, and check that they raise exceptions when
        appropriate.
        """

        # Check unsubscribing a ticker that isn't
        # in the price handler list
        # ToFix: https://github.com/mhallsmoore/qstrader/issues/46
        # self.assertRaises(
        #     KeyError, lambda: self.price_handler.unsubscribe_ticker("PG")
        # )

        # Check a ticker that is already subscribed
        # to make sure that it doesn't raise an exception
        try:
            self.price_handler.subscribe_ticker("GOOG")
        except Exception as E:
            self.fail("subscribe_ticker() raised %s unexpectedly" % E)

        # Subscribe a new ticker, without CSV
        # ToFix: https://github.com/mhallsmoore/qstrader/issues/46
        # self.assertRaises(
        #     IOError, lambda: self.price_handler.subscribe_ticker("XOM")
        # )

        # Unsubscribe a current ticker
        self.assertTrue("GOOG" in self.price_handler.tickers)
        self.assertTrue("GOOG" in self.price_handler.tickers_data)
        self.price_handler.unsubscribe_ticker("GOOG")
        self.assertTrue("GOOG" not in self.price_handler.tickers)
        self.assertTrue("GOOG" not in self.price_handler.tickers_data)

    def test_get_best_bid_ask(self):
        """
        Tests that the 'get_best_bid_ask' method produces the
        correct values depending upon validity of ticker.
        """
        bid, ask = self.price_handler.get_best_bid_ask("AMZN")
        self.assertEqual(PriceParser.display(bid, 5), 502.10001)
        self.assertEqual(PriceParser.display(ask, 5), 502.11999)

        bid, ask = self.price_handler.get_best_bid_ask("C")
        # TODO WHAT TO DO HERE?.
        # self.assertEqual(PriceParser.display(bid, 5), None)
        # self.assertEqual(PriceParser.display(ask, 5), None)


if __name__ == "__main__":
    unittest.main()
