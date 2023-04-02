import logging
import logging.handlers
import sys
import threading

import board
import adafruit_aw9523
import adafruit_seesaw.seesaw

from lcd1602rgb import RGB1602
from menuchooser import MenuChooser

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

logger = logging.getLogger()

fileHandler = logging.handlers.RotatingFileHandler("menu.log", maxBytes=1024*1024, backupCount=5)
fileHandler.setLevel(logging.INFO)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
logger.addHandler(consoleHandler)

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
consoleHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)

logger.setLevel(logging.DEBUG)
logger.info("----------------------------")
logger.info("Menu selector starting")

sys.excepthook = handle_exception
threading.excepthook = handle_exception

i2c_lock = threading.Lock()

lcd = RGB1602(col=16, row=2, i2c_lock=i2c_lock)
lcd.setRGB(64, 128, 64)
lcd.print_line1(f"Select version")

i2c = board.I2C()

# Turn off all the lights
aw9523 = adafruit_aw9523.AW9523(i2c)
illuminated_button_aw9523_ids = (1, 2, 3, 4, 5, 6, 7)
for led_id in illuminated_button_aw9523_ids:
    aw9523.LED_modes = aw9523.LED_modes | 1 << led_id
    aw9523.set_constant_current(led_id, 0)

# Set up the rotary controller
rotary2_seesaw = adafruit_seesaw.seesaw.Seesaw(i2c, 0x37)

menu_items = sys.argv[1:]
menu = MenuChooser(menu_items, rotary2_seesaw, 8, 7, lcd)

index, choice = menu.wait_for_selection()
logger.info(f"Menu choice was {[index]}: {choice}")
sys.exit(index)