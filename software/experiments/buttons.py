import functools
import gpiozero
import signal
import time

class IlluminatedButton():
    def __init__(self, button_pin=None, led_pin=None):
        self.button = gpiozero.Button(button_pin) if button_pin else None
        self.led = gpiozero.LED(led_pin) if led_pin else None

    def on(self):
        if self.led: self.led.on()

    def off(self):
        if self.led: self.led.off()

    @property
    def when_pressed(self):
        return self.button.when_pressed

    @when_pressed.setter
    def when_pressed(self, value):
        self.button.when_pressed = value

def button_pressed(index, button):
    print(f"Button pressed: {index}")

buttons = (
    IlluminatedButton(14,    7),
    IlluminatedButton(15,   12),
    IlluminatedButton(18,   16),
    IlluminatedButton(23,   26),
    IlluminatedButton(24, None),
    IlluminatedButton(25, None),
    IlluminatedButton( 8, None),
)

for index, button in enumerate(buttons):
    button.when_pressed = functools.partial(button_pressed, index)

b0, b1, b2, b3 = (buttons[0], buttons[1], buttons[2], buttons[3])

while True:
    b0.on()
    b1.off()
    b2.on()
    b3.off()
    time.sleep(0.5)
    b0.off()
    b1.on()
    b2.off()
    b3.on()
    time.sleep(0.5)

signal.pause()