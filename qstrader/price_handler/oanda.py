from .base import AbstractBarPriceHandler
from ..event import BarEvent

import requests
from collections import deque
from urllib import parse
from datetime import datetime, timedelta

oanda_request_date_format_string = '%Y-%m-%dT%H:%M:%SZ'
oanda_RFC3339_format = '%Y-%m-%dT%H:%M:%S.000000Z'


class OandaBarPriceHandler(AbstractBarPriceHandler):
    """
    OandaBarPriceHandler..
    """
    def __init__(self, instrument, granularity,
                 start: datetime, end: datetime,
                 daily_alignment=0, alignment_timezone=None,
                 warmup_bar_count=0,
                 server=None, bearer_token=None,
                 events_queue=None):
        if len(instrument) == 6:
            self.instrument = instrument[:3] + "_" + instrument[3:]
        else:
            self.instrument = instrument
        self.granularity = granularity
        self.start_date = start
        self.end_date = end
        self.daily_alignment = daily_alignment
        self.alignment_timezone = alignment_timezone
        self.warmup_bar_count = warmup_bar_count
        # self.warmup_bar_counter = warmup_bar_count

        self.server = server
        self.bearer_token = f"Bearer {bearer_token}"
        self.request_headers = {
            'Authorization': self.bearer_token,
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip, deflate',
            'Content-type': 'application/x-www-form-urlencoded'
        }

        self.events_queue = events_queue
        self.continue_backtest = True

        self.next_start_date = start
        self.candle_queue = deque()
        self.last_candle_time = ''
        self.candle_timespan = timedelta(
            seconds=self._granularity_to_seconds()
        )

        if warmup_bar_count > 0:
            # request warmup items (note: max 5000)

            start_string = self.start_date.strftime(
                oanda_request_date_format_string
            )

            url = (
                f"https://{self.server}/v1/candles"
                f"?instrument={parse.quote_plus(self.instrument)}"
                f"&granularity={self.granularity}"
                f"&count={self.warmup_bar_count}"
                f"&end="
                f"{parse.quote_plus(start_string)}"  # grab bars up to the
                                                     # start date
                f"&candleFormat=midpoint"
                f"&dailyAlignment={self.daily_alignment}"
                f"&alignmentTimezone="
                f"{parse.quote_plus(self.alignment_timezone)}"
            )
            response_json = requests.get(url, headers=self.request_headers)
            self.candle_queue.extend(response_json.json()['candles'])

    def _granularity_to_seconds(self):
        if self.granularity == 'D':
            return 86400  # Seconds in a day
        return None

    def _create_event(self, candle):
        return BarEvent(
            ticker=self.instrument,
            time=candle['time'],
            period=self._granularity_to_seconds(),
            open_price=candle['openMid'],
            high_price=candle['highMid'],
            low_price=candle['lowMid'],
            close_price=candle['closeMid'],
            volume=candle['volume']
        )

    def _pop_candle_onto_event_queue(self):
        if len(self.candle_queue) > 0:
            candle = self.candle_queue.popleft()
            bar_event = self._create_event(candle)
            self.events_queue.put(bar_event)
        else:
            self.events_queue.put(None)

    def _fetch_more_candles(self):

        start_string = self.next_start_date.strftime(
            oanda_request_date_format_string
        )

        url = (
            f"https://{self.server}/v1/candles"
            f"?instrument={parse.quote_plus(self.instrument)}"
            f"&granularity={self.granularity}"
            f"&count=5000"
            f"&start={parse.quote_plus(start_string)}"
            f"&candleFormat=midpoint"
            f"&dailyAlignment={self.daily_alignment}"
            f"&alignmentTimezone="
            f"{parse.quote_plus(self.alignment_timezone)}"
        )

        response_json = requests.get(url, headers=self.request_headers)
        response_dict = response_json.json()

        # filter out incomplete and already queued candles
        candles = list(filter(
            lambda x:
                x['complete'] and
                x['time'] > self.last_candle_time and
                x['time'] < self.end_date.strftime(oanda_RFC3339_format),
            response_dict['candles']
        ))

        if len(candles) > 0:
            self.candle_queue.extend(candles)
            self.last_candle_time = candles[-1]['time']
            self.next_start_date = datetime.strptime(
                candles[-1]['time'],
                oanda_RFC3339_format
            ) + self.candle_timespan
        else:
            # self.events_queue.put(None)

            # either we have to wait for a new candle to become available (live
            # scenario) or we have to jump forward over a gap in candles (e.g.
            # a weekend, back test scenario)

            if self.next_start_date + self.candle_timespan > datetime.utcnow():
                return

            self.next_start_date += self.candle_timespan * 5000
            if self.next_start_date > self.end_date:
                self.continue_backtest = False

    def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """
        if len(self.candle_queue) > 0:
            self._pop_candle_onto_event_queue()
        else:
            if (self.next_start_date > datetime.now() or
                    self.next_start_date > self.end_date):
                self.continue_backtest = False
                return

            self._fetch_more_candles()
            self._pop_candle_onto_event_queue()
