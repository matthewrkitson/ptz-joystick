class Recaller():
  def __init__(self, keypad, recall_button, set_button, camera, lcd):
    self.keypad = keypad
    self.recall_button = recall_button
    self.set_button = set_button
    self.camera = camera
    self.lcd = lcd

    self.keypad.keypress_handler = self.keypress_handler

  def keypress_handler(self, key):
      self.lcd.print_line1(f"Keypress: {key}")
