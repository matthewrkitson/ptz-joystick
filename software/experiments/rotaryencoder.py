# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT

"""I2C rotary encoder NeoPixel color picker and brightness setting example."""
import board
from rainbowio import colorwheel
from adafruit_seesaw import seesaw, neopixel, rotaryio, digitalio

import gpiozero
import signal
import time


# For use with the STEMMA connector on QT Py RP2040
# import busio
# i2c = busio.I2C(board.SCL1, board.SDA1)
# seesaw = seesaw.Seesaw(i2c, 0x36)

# i2c_address = 0x36
# int_pin_gpio = 25

i2c_address = 0x37
int_pin_gpio = 8

seesaw = seesaw.Seesaw(board.I2C(), i2c_address)

encoder = rotaryio.IncrementalEncoder(seesaw)
seesaw.enable_encoder_interrupt()
seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
switch = digitalio.DigitalIO(seesaw, 24)

pixel = neopixel.NeoPixel(seesaw, 6, 1)
pixel.brightness = 0.5

position = 0
color = 0  # start at red

def read_position():
    global color, position, switch
    print("reading position")

    # negate the position to make clockwise rotation positive
    delta = seesaw.encoder_delta()
    print(f"Delta: {delta}")
    if delta: 
        position -= delta
        print(f"New Position: {position}")
        if switch.value:
            color = (color + 256 - delta) % 256  # wrap around to 0-256
            pixel.fill(colorwheel(color))
        else: 
            new_brightness = max(min(pixel.brightness + (delta / 50), 1), 0)
            pixel.brightness = new_brightness

int_pin = gpiozero.Button(int_pin_gpio, pull_up=None, active_state=False)
# int_pin.when_pressed = read_position

print("Turn the encoder")

while True:
    time.sleep(0.1)
    try:
        if int_pin.value:
            read_position()
        else:
            continue
    except:
        pass

signal.pause()
