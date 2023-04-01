import gpiozero
import logging
import threading

from adafruit_seesaw import seesaw, neopixel, digitalio

class MenuChooser():
    def __init__(self, items, seesaw, int_pin_gpio, encoder_press_button_gpio, lcd):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Creating menu chooser object")
        self.items = items
        self.seesaw = seesaw
        self.lcd = lcd
        self.int_pin = gpiozero.Button(int_pin_gpio, pull_up=None, active_state=False, hold_time=0.1)
        self.encoder_press_button = gpiozero.Button(encoder_press_button_gpio, pull_up=True)

        self.seesaw.enable_encoder_interrupt()
        self.seesaw.pin_mode(24, seesaw.INPUT_PULLUP)

        self.button = digitalio.DigitalIO(seesaw, 24)
        self.pixel = neopixel.NeoPixel(seesaw, 6, 1)
        self.pixel.brightness = 0.5

        # We have to trigger on hold as well as on press because if we're not
        # quick enough at handling the press and the interrupt line goes active
        # again while we're still dealing with it, gpiozero will not call the
        # when_pressed function again, and we'll never handle the new 
        # interrupt, no matter how much we twist the dial. 
        self.int_pin.when_pressed = self.menu_item_changed
        self.int_pin.when_held = self.menu_item_changed
        self.encoder_press_button.when_pressed = self.menu_item_selected

        self.item_selected_event = threading.Event()

        self.index = 0
        self.update_display()

        # Set up a mutex/signal/semaphore here that we can wait on later

    def menu_item_changed(self):
        # Negate the position to make clockwise rotation positive
        delta = -self.seesaw.encoder_delta()
        new_index = (self.index + delta) % len(self.items)
        self.logger.debug(f"index: {self.index}, delta: {delta}, new index: {new_index}")
        self.index = new_index
        self.update_display()

    def update_display(self):
        self.logger.debug(f"{self.index}: {self.items[self.index]}")
        self.lcd.print_line2(self.items[self.index])

    def menu_item_selected(self):
        self.logger.debug(f"Menu item selected: {self.index}: {self.items[self.index]}")
        self.logger.debug(f"Menu selection event set")
        self.item_selected_event.set()

    def wait_for_selection(self):
        self.item_selected_event.wait()
        self.logger.debug(f"Menu selection event received")
        self.logger.debug(f"Menu item selected: {self.index}: {self.items[self.index]}")
        return (self.index, self.items[self.index])

