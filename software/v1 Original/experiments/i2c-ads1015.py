# https://docs.circuitpython.org/projects/ads1x15/en/latest/

import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
# Make sure you've enabled i2c on the Pi first
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1015(i2c)

# Create single-ended inputs on all channels
chan1 = AnalogIn(ads, ADS.P0)
chan2 = AnalogIn(ads, ADS.P1)
chan3 = AnalogIn(ads, ADS.P2)
chan4 = AnalogIn(ads, ADS.P3)

# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)

print("{:>5}\t{:>5}\t{:>5}\t{:>5}".format('v1', 'v2', 'v3', 'v4'))

while True:
    print("{:>5}\t{:>5.3f}\t{:>5.3f}\t{:>5.3f}".format(chan1.value, chan2.voltage, chan3.voltage, chan4.voltage))
    time.sleep(0.5)