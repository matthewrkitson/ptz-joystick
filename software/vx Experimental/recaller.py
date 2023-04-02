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

        # Ignore #
        elif key == "#":
            return

        # All other keys are themselves
        else:
            self.buffer += f"{key}"

        self._update_display()

    def set_handler(self):
        logging.debug(f"Recaller set handler: {self.buffer}")
        if self.buffer:
            try:
                preset_id = self._get_preset_id()
                if self._is_valid_preset_id(preset_id):
                    self.camera.store_preset(preset_id)
                    self.lcd.print_line1("")
                    self.lcd.print_line2(f"Set {preset_id}")
                else: 
                    logging.error(f"Attempted to set invalid preset_id: {preset_id}")
                    self.lcd.print_line1("Invalid preset")
                    self.lcd.print_line2(f"{preset_id}")
            except:
                logging.exception("Exception in Recaller set handler")
                self.lcd.print_line1("Error setting")
                self.lcd.print_line2(f"preset")
            finally:
                self.buffer = ""
                self._stop_pulsing()

    def recall_handler(self):
        logging.debug(f"Recaller recall handler: {self.buffer}")
        if self.buffer:
            try:
                preset_id = self._get_preset_id()
                if self._is_valid_preset_id(preset_id):
                    self.camera.recall_preset(preset_id)
                    self.lcd.print_line1("")
                    self.lcd.print_line2(f"Recalled {preset_id}")
                else:
                    logging.error(f"Attempted to set invalid preset_id: {preset_id}")
                    self.lcd.print_line1("Invalid preset")
                    self.lcd.print_line2(f"{preset_id}")
            except:
                logging.exception("Exception in Recaller recall handler")
                self.lcd.print_line1("Error recalling")
                self.lcd.print_line2(f"preset")
            finally:
                self.buffer = ""
                self._stop_pulsing()

    def _start_pulsing(self):
        self.set_button.pulse()
        self.recall_button.pulse()

    def _stop_pulsing(self):
        self.recall_button.off()
        self.set_button.off()

    def _is_pulsing(self):
        return (self.recall_button.state == IlluminatedButton.PULSING or
                self.recall_button.state == IlluminatedButton.ON)

    def _get_preset_id(self):
        preset_id = None
        try:
            preset_id = int(self.buffer)
        except:
            logging.exception(f"Unable to convert {self.buffer} to int")
        
        return preset_id
            
    def _is_valid_preset_id(self, preset_id):
        return (preset_id >= 0 and preset_id <= 89 
                or
                preset_id >= 100 and preset_id <= 254)

    def _update_display(self):
        if self.buffer:
            self.lcd.print_line1(f"Preset: {self.buffer}")
            self.lcd.print_line2("")

            # If the preset id is valid and we're not already pulsing, start pulsing
            preset_id = self._get_preset_id()
            if self._is_valid_preset_id(preset_id) and not self._is_pulsing():
                self._start_pulsing()

            # If the preset id is invalid and we are already pulsing, stop pulsing.
            if not self._is_valid_preset_id(preset_id) and self._is_pulsing():
                self._stop_pulsing()

        else:
            # Buffer is empty. Clear screen and stop pulsing
            self._stop_pulsing()
            self.lcd.print_line1("")
            self.lcd.print_line2("")