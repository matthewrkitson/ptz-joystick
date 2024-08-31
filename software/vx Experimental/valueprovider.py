import abc

import utils

class ValueProvider():
    def __init__(self, value, min, max):
        self._value = value
        self._min = min
        self._max = max
        self._value_changed = None

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = utils.clamp(value, self._min, self._max)
        if self._value_changed:
            self._value_changed()

    def get_range(self):
        return (self._min, self._max)

    def get_min(self):
        return self._min

    def get_max(self):
        return self._max

    def get_value_changed(self):
        return self._value_changed

    def set_value_changed(self, callback):
        self._value_changed = callback

    value = property(get_value, set_value)
    range = property(get_range)
    min = property(get_min)
    max = property(get_max)
    value_changed = property(get_value_changed, set_value_changed)