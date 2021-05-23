# -*- coding: utf-8 -*-

"""A very simple implementation of Time Series with durations in values

Use a pre-allocated n*2 numpy array for storage:
* on first row: timestamps (epoch)
* on second row: durations (ms)


"""

import numpy as np
from datetime import datetime

_DEFAULT_MAXSIZE = 10*1024*1024


class TimeSeries(object):
    """To be completed

    Attributes:
       maxsize: maximum size
    """

    def __init__(self, maxsize=_DEFAULT_MAXSIZE):
        self.maxsize = maxsize
        # array is pre-allocated for performance reasons
        self._array = np.zeros((2, maxsize), int)
        self._size = 0

    def size(self):
        return self._size

    def append(self, time, value):
        self._array[0, self._size] = time
        self._array[1, self._size] = value
        self._size += 1
        if self._size > self.maxsize:
            raise Exception('TimeSeries Overflow')

    def stats(self):
        if self._size == 0:
            return None
        times = self._array[0, 0:self._size]
        values = self._array[1, 0:self._size]
        maxdur = np.amax(values)
        return {'from': datetime.fromtimestamp(np.amin(times)/1000.0)
                .isoformat(),
                'to': datetime.fromtimestamp((np.amax(times)+maxdur)/1000.0)
                .isoformat(),
                'count': self._size,
                'median': int(np.median(values)),
                'perc95': int(np.percentile(values, 95)),
                'max': maxdur
                }
