import abc

import utils

class ValueProvider():
    def __init__(self, value, min, max):
        self._value = value
        self._min = min
        self._max = max

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = utils.clamp(value, self._min, self._max)

    def get_range(self):
        return (self._min, self._max)

    def get_min(self):
        return self._min

    def get_max(self):
        return self._max

    value = property(get_value, set_value)
    range = property(get_range)
    min = property(get_min)
    max = property(get_max)