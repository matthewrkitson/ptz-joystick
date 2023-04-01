import utils

from valueprovider import ValueProvider

class ConstantValueProvider(ValueProvider):
    def __init__(self, value, min, max):
        super().__init__(min, max)
        self._value = utils.clamp(value, min, max)

    @property
    def value(self):
        return self._value
