import gpiozero
import functools
import logging
import logging.handlers
import subprocess
import sys
import threading

import board
import digitalio
import adafruit_aw9523
import adafruit_ads1x15.ads1015
import adafruit_seesaw.seesaw

from analogin import AnalogIn
from analogjoystick import AnalogJoystick
from constantvalueprovider import ConstantValueProvider
from digitaljoystick import DigitalJoystick
from focusser import Focusser
from illuminatedbutton import IlluminatedButton
from keypad import Keypad
from lcd1602rgb import RGB1602
from menuchooser import MenuChooser
from quitter import Quitter
from recaller import Recaller
from rotaryvalueprovider import RotaryValueProvider
from zoomer import Zoomer

import web_api

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
logger.info("   Menu selector starting   ")
logger.info("----------------------------")

sys.excepthook = handle_exception
threading.excepthook = handle_exception

i2c_lock = threading.Lock()

lcd = RGB1602(col=16, row=2, i2c_lock=i2c_lock)
lcd.setRGB(64, 128, 64)
lcd.print_line1(f"Select version")

i2c = board.I2C()
aw9523 = adafruit_aw9523.AW9523(i2c)

rotary2_seesaw = adafruit_seesaw.seesaw.Seesaw(board.I2C(), 0x37)
menu_items = ("Apples", "Bananas", "Cherry", "Danson Plum", "Elderberry", "Fig")
menu = MenuChooser(menu_items, rotary2_seesaw, 8, 7, lcd)

rotary1_int_pin = gpiozero.Button(25, pull_up=None, active_state=False)
rotary1_seesaw = adafruit_seesaw.seesaw.Seesaw(board.I2C(), 0x36)

preset_recall_button = IlluminatedButton(20, aw9523, 1, i2c_lock)
preset_store_button  = IlluminatedButton(21, aw9523, 2, i2c_lock)
zoom_in_button       = IlluminatedButton(26, aw9523, 3, i2c_lock)
zoom_out_button      = IlluminatedButton(19, aw9523, 4, i2c_lock)
focus_in_button      = IlluminatedButton(13, aw9523, 5, i2c_lock)
focus_lock_button    = IlluminatedButton( 6, aw9523, 6, i2c_lock)
focus_out_button     = IlluminatedButton( 5, aw9523, 7, i2c_lock)

joystick_up_button    = gpiozero.Button(14)
joystick_down_button  = gpiozero.Button(15)
joystick_left_button  = gpiozero.Button(18)
joystick_right_button = gpiozero.Button(23)

keypad = Keypad((4, 17, 27), (22, 10, 9, 11))

index, choice = menu.wait_for_selection()
logger.info(f"Menu choice was {[index]}: {choice}")
sys.exit(index)