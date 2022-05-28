import logging

from illuminatedbutton import IlluminatedButton

class Recaller():
    def __init__(self, keypad, recall_button, set_button, camera, lcd):
        self.keypad = keypad
        self.keypad.keypress_handler = self.keypress_handler

        self.recall_button = recall_button
        self.recall_button.when_pressed = self.recall_handler

        self.set_button = set_button
        self.set_button.when_pressed = self.set_handler

        self.camera = camera
        self.lcd = lcd

        self.buffer = ""

    def keypress_handler(self, key):
        logging.debug(f"Recaller keypress handler: {key}")

        # * is backspace
        if key == "*":
            self.buffer = self.buffer[:-1]

        # Don't allow an arbitrarily long entry
        elif len(self.buffer) > 5:
            return

        # All other keys are themselves
        else:
            self.buffer += f"{key}"

        self._update_display()

    def set_handler(self):
        logging.debug(f"Recaller set handler: {self.buffer}")
        if self.buffer:
            try:
                preset_id = int(self.buffer)
                self.camera.store_preset(preset_id)
                self.buffer = ""
            except:
                logging.exception("Exception in Recaller set handler")
            finally:
                self._update_display()

    def recall_handler(self):
        logging.debug(f"Recaller recall handler: {self.buffer}")
        if self.buffer:
            try:
                preset_id = int(self.buffer)
                self.camera.recall_preset(preset_id)
                self.buffer = ""
            except:
                logging.exception("Exception in Recaller recall handler")
            finally:
                self._update_display()

        
    def _update_display(self):
        if self.buffer:
            self.lcd.print_line1(f"Preset: {self.buffer}")
            self.lcd.print_line2("")

            # If this is the first character, start pulsing
            # (if we're already pulsing, it's because we've backspaced to just
            # one character left; no need to restart pulsing in that case)
            if len(self.buffer) == 1 and not self.recall_button.state == IlluminatedButton.PULSING:
                self.set_button.pulse()
                self.recall_button.pulse()

        else:
            # Buffer is empty. Clear screen and stop pulsing
            self.recall_button.off()
            self.set_button.off()
            self.lcd.print_line1("")
            self.lcd.print_line2("")