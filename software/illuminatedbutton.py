import gpiozero

class IlluminatedButton(gpiozero.Button):
    def __init__(self, button_pin, aw9523, led_id, i2c_lock):
        gpiozero.Button.__init__(self, button_pin)
        self.aw9523 = aw9523
        self.led_id = led_id
        self.i2c_lock = i2c_lock

        with self.i2c_lock:
            self.aw9523.LED_modes = aw9523.LED_modes | 1 << led_id
            self.aw9523.set_constant_current(led_id, 0)

    def on(self):
        with self.i2c_lock:
            self.aw9523.set_constant_current(self.led_id, 255)

    def off(self):
        with self.i2c_lock:
            self.aw9523.set_constant_current(self.led_id, 255)
