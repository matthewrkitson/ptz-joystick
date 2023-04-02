import adafruit_ads1x15.ads1015
import adafruit_ads1x15.analog_in

class AnalogIn():
    def __init__(self, ads1015, pin, i2c_lock):
        self.analog_in = adafruit_ads1x15.analog_in.AnalogIn(ads1015, pin)
        self.i2c_lock = i2c_lock

    P0 = adafruit_ads1x15.ads1015.P0
    P1 = adafruit_ads1x15.ads1015.P1
    P2 = adafruit_ads1x15.ads1015.P2
    P3 = adafruit_ads1x15.ads1015.P3

    @property
    def value(self):
        """Returns the value of an ADC pin as an integer."""
        with self.i2c_lock:
            return self.analog_in.value

    @property
    def voltage(self):
        """Returns the voltage from the ADC pin as a floating point value."""
        with self.i2c_lock:
            return self.analog_in.voltage

    @property
    def voltage_max(self):
        return 3.3

    @property
    def voltage_min(self):
        return 0
