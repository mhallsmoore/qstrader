import unittest
import os
import datetime
import sys

from qstrader.compat import queue
from qstrader.price_handler.oanda import OandaBarPriceHandler


class TestOandaBarPriceHandler(unittest.TestCase):
    def test_warmup(self):
        OANDA_API_ACCESS_TOKEN = os.environ.get('OANDA_API_ACCESS_TOKEN', None)
        events_queue = queue.Queue()
        oanda_bar_price_handler = OandaBarPriceHandler(
            instrument='EURUSD', granularity='D',
            start=datetime.date(2016, 1, 1),
            end=datetime.date(2016, 12, 31),
            daily_alignment=0,
            alignment_timezone='Europe/Paris',
            warmup_bar_count=1,
            server='api-fxpractice.oanda.com',
            bearer_token=OANDA_API_ACCESS_TOKEN,
            events_queue=events_queue
        )

        oanda_bar_price_handler.stream_next()

        event = events_queue.get(False)
        self.assertEqual(event.open_price, 1.09266)

    def test_no_warmup(self):
        OANDA_API_ACCESS_TOKEN = os.environ.get('OANDA_API_ACCESS_TOKEN', None)
        events_queue = queue.Queue()

        oanda_bar_price_handler = OandaBarPriceHandler(
            instrument='EURUSD', granularity='D',
            start=datetime.datetime(2016, 1, 1),
            end=datetime.datetime(2016, 12, 31),
            daily_alignment=0,
            alignment_timezone='Europe/Paris',
            warmup_bar_count=0,
            server='api-fxpractice.oanda.com',
            bearer_token=OANDA_API_ACCESS_TOKEN,
            events_queue=events_queue
        )

        oanda_bar_price_handler.stream_next()
        self.assertEqual(len(oanda_bar_price_handler.candle_queue), 309)
        event = events_queue.get(False)
        self.assertEqual(event.open_price, 1.08743)

    # def test_continue_backtest_set(self):


if __name__ == "__main__":
    unittest.main()
