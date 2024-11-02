import gpiozero
import threading
import time

class IlluminatedButton(gpiozero.Button):
    MIN_PULSE_BRIGHTNESS = 0
    MAX_PULSE_BRIGHTNESS = 255
    ON = "on"
    OFF = "off"
    PULSING = "pulsing"

    def __init__(self, button_pin, aw9523, led_id, i2c_lock):
        gpiozero.Button.__init__(self, button_pin)
        self.aw9523 = aw9523
        self.led_id = led_id
        self.i2c_lock = i2c_lock
        self.stop_pulsing = False
        self.pulse_thread = None

        with self.i2c_lock:
            self.aw9523.LED_modes = aw9523.LED_modes | 1 << led_id
            self.aw9523.set_constant_current(led_id, 0)

        self.state = IlluminatedButton.OFF

    def on(self):
        self._stop_pulsing()
        with self.i2c_lock:
            self.aw9523.set_constant_current(self.led_id, 155)
        self.state = IlluminatedButton.ON

    def pulse(self, period=1):
        # TODO: Get pulsing working properly
        self.on()

        # self._stop_pulsing()
        # self.pulse_thread = threading.Thread(target=self._pulse, args=(period,), name=f"pulse_thread for LED {self.led_id}", daemon=True)
        # self.stop_pulsing = False
        # self.pulse_thread.start()
        # self.state = IlluminatedButton.PULSING

    def off(self):
        self._stop_pulsing()
        with self.i2c_lock:
            self.aw9523.set_constant_current(self.led_id, 0)
        self.state = IlluminatedButton.OFF

    def _pulse(self, period):
        # TODO: Use a non-linear brightness compensation function 
        # TODO: Support min and max brightness levels
        while not self.stop_pulsing:
            for brightness in range(256):
                if self.stop_pulsing: break
                self.aw9523.set_constant_current(self.led_id, brightness)
                time.sleep(0.1)
            for brightness in range(256):
                if self.stop_pulsing: break
                self.aw9523.set_constant_current(self.led_id, 255 - brightness)
                time.sleep(0.1)

    def _stop_pulsing(self):
        if self.pulse_thread:
            self.stop_pulsing = True
            self.pulse_thread.join()
            self.pulse_thread = None

