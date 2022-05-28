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

from analogin import AnalogIn
from analogjoystick import AnalogJoystick
from digitaljoystick import DigitalJoystick
from focusser import Focusser
from illuminatedbutton import IlluminatedButton
from keypad import Keypad
from lcd1602rgb import RGB1602
from quitter import Quitter
from recaller import Recaller
from zoomer import Zoomer

import web_api

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

logger = logging.getLogger()

fileHandler = logging.handlers.RotatingFileHandler("ptz-joystick.log", maxBytes=1024*1024, backupCount=5)
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
logger.info("PTZ joystick camera starting")
logger.info("----------------------------")

sys.excepthook = handle_exception
threading.excepthook = handle_exception

camera = web_api.WebApiController("localhost:8080")

network_info = subprocess.check_output(["ip", "address"], text=True)
logging.info(f"Network status:\n{network_info}")

i2c_lock = threading.Lock()

lcd = RGB1602(16, 2, i2c_lock)
lcd.setRGB(64, 128, 64)
lcd.print_line1(f"PTZ camera")

i2c = board.I2C()
aw9523 = adafruit_aw9523.AW9523(i2c)

ads1015 = adafruit_ads1x15.ads1015.ADS1015(i2c)
analog_joystick_horizontal = AnalogIn(ads1015, AnalogIn.P0, i2c_lock)
speed_dial = AnalogIn(ads1015, AnalogIn.P1, i2c_lock)
analog_joystick_vertical = AnalogIn(ads1015, AnalogIn.P2, i2c_lock)
speed_slider = AnalogIn(ads1015, AnalogIn.P3, i2c_lock)

preset_recall_button = IlluminatedButton(14, aw9523, 1, i2c_lock)
preset_store_button  = IlluminatedButton(15, aw9523, 2, i2c_lock)
zoom_in_button       = IlluminatedButton(18, aw9523, 3, i2c_lock)
zoom_out_button      = IlluminatedButton(23, aw9523, 4, i2c_lock)
focus_in_button      = IlluminatedButton(24, aw9523, 5, i2c_lock)
focus_auto_button    = IlluminatedButton(25, aw9523, 6, i2c_lock)
focus_out_button     = IlluminatedButton( 8, aw9523, 7, i2c_lock)

joystick_up_button    = gpiozero.Button( 4)
joystick_down_button  = gpiozero.Button(17)
joystick_left_button  = gpiozero.Button(27)
joystick_right_button = gpiozero.Button(22)

keypad = Keypad((19, 13, 6), (5, 11, 9, 10))

quitter = Quitter(preset_recall_button, preset_store_button, lcd)
zoomer = Zoomer(zoom_in_button, zoom_out_button, camera, lcd)
focusser = Focusser(focus_in_button, focus_out_button, focus_auto_button, camera, lcd)
digital_joystick = DigitalJoystick(joystick_up_button, joystick_down_button, joystick_left_button, joystick_right_button, speed_slider, camera, lcd)
analog_joystick = AnalogJoystick(analog_joystick_vertical, analog_joystick_horizontal, camera, lcd)
recaller = Recaller(keypad, preset_recall_button, preset_store_button, camera, lcd)

# analog_joystick.message_loop()

quitter.wait_for_exit()

logger.info("PTZ joystick camera stopping")
