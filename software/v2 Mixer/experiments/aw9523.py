import board
import digitalio
import adafruit_aw9523

import signal
import time

i2c = board.I2C()
aw = adafruit_aw9523.AW9523(i2c)

aw.LED_modes = 0b0000000011111110
pins = [aw.get_pin(p + 1) for p in range(7)]

for index, pin in enumerate(pins):
    pin.switch_to_output()
    aw.set_constant_current(index + 1, 0)
    pin.value = True


while True:
    for index in range(7):
        for current in range(256):
            aw.set_constant_current(index + 1, current)
            time.sleep(0.001)
        for current in range(256):
            aw.set_constant_current(index + 1, 255 - current)
            time.sleep(0.001)

signal.pause()