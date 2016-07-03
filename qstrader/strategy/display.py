#!/usr/bin/env/python

import time

from .base import AbstractStrategy
from ..profiling import s_speed
from ..event import EventType


class DisplayStrategy(AbstractStrategy):
    """
    A strategy which display ticks / bars

    params:
        n = 10000
        n_window = 5
    """
    def __init__(self, n=100, n_window=5):
        self.n = n
        self.n_window = n_window
        self.t0 = time.time()
        self.i = 0

    def calculate_signals(self, event):
        if event.type in [EventType.TICK, EventType.BAR]:
            if self.i % self.n == 0 and self.i != 0:
                print(s_speed(event, self.i, self.t0))
                print("")
            if self.i % self.n in range(self.n_window):
                print("%d %s" % (self.i, event))
            self.i += 1
