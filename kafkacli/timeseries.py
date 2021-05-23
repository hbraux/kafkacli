# -*- coding: utf-8 -*-

"""A very simple implementation of Time Series with durations in values

Use a pre-allocated arrays for storage:


"""

from datetime import datetime

_DEFAULT_MAXSIZE = 1024*1024


class TimeSeries(object):
    """To be completed

    Attributes:
       maxsize: maximum size
    """

    def __init__(self, maxsize=_DEFAULT_MAXSIZE):
        self.maxsize = maxsize
        # array is pre-allocated for performance reasons
        self._array_ts = [0] * maxsize
        self._array_val = [0] * maxsize
        self._size = 0

    def size(self):
        return self._size

    def append(self, time, value):
        self._array_ts[self._size] = time
        self._array_ts[self._size] = value
        self._size += 1
        if self._size > self.maxsize:
            raise Exception('TimeSeries Overflow')

    def stats(self):
        if self._size == 0:
            return None
        print("NOT IMPLEMENTED YET")
