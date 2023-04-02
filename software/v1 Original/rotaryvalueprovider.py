from valueprovider import ValueProvider
from adafruit_seesaw import neopixel, digitalio

import logging
import threading
import time

import utils

class RotaryValueProvider(ValueProvider):
    def __init__(self, min, max, description, seesaw, int_pin, lcd):
        super().__init__(min, min, max)
        self.description = description
        self.seesaw = seesaw
        self.lcd = lcd
        self.int_pin = int_pin

        seesaw.enable_encoder_interrupt()
        seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
        
        self.switch = digitalio.DigitalIO(seesaw, 24)

        self.pixel = neopixel.NeoPixel(seesaw, 6, 1)
        self.pixel.brightness = 0.5

        # Start a new thread to run the message loop
        self.poller_loop_thread = threading.Thread(target=self.poller_loop, daemon=True)
        self.poller_loop_thread.start()
    
    def poller_loop(self):
        while True:
            time.sleep(0.1)
            try:
                if not self.int_pin.value:
                    continue

                # Negate the delta to make clockwise rotation positive
                delta = -self.seesaw.encoder_delta()
                if delta:
                    self.set_value(self.value + delta)
                    self.lcd.print_line1(f"{self.description}: {self.value}")
                    self.lcd.print_line2(f"")

            except: 
                logging.exception("Exception from rotary value provider")
                self.lcd.print_line1("Encoder error")
                self.lcd.print_line2(f"")
