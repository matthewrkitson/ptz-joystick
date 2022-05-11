import gpiozero

class IlluminatedButton():
    def __init__(self, button_pin=None, led_pin=None):
        self.button = gpiozero.Button(button_pin) if button_pin else None
        self.led = gpiozero.LED(led_pin) if led_pin else None

    def on(self):
        if self.led: self.led.on()

    def off(self):
        if self.led: self.led.off()

    @property
    def is_pressed(self):   
        return self.button.is_pressed if self.button else False

    @property
    def when_pressed(self):
        return self.button.when_pressed if self.button else None

    @when_pressed.setter
    def when_pressed(self, value):
        if self.button:
            self.button.when_pressed = value

    @property
    def when_held(self):
        return self.button.when_held if self.button else None

    @when_held.setter
    def when_held(self, value):
        if self.button:
            self.button.when_held = value