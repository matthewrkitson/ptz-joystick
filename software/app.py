import functools
import logging
import logging.handlers
import subprocess

import board
import digitalio
import adafruit_aw9523

from illuminatedbutton import IlluminatedButton
from lcd1602rgb import RGB1602
from focusser import Focusser
from quitter import Quitter
from zoomer import Zoomer

import web_api

def preset_recall(camera, lcd):
    lcd.print_line1("Preset recall")

def preset_store(camera, lcd):
    lcd.print_line1("Preset store")

def focus_in(camera, lcd):
    lcd.print_line1("Focus in")

def focus_out(camera, lcd):
    lcd.print_line1("Focus out")

def focus_auto(camera, lcd):
    lcd.print_line1("Auto focus")

logger = logging.getLogger(__name__)

fileHandler = logging.handlers.RotatingFileHandler("ptz-joystick.log", maxBytes=1024*1024, backupCount=5)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
consoleHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)

logger.setLevel(logging.DEBUG)
logger.info("PTZ joystick camera starting")

camera = web_api.WebApiController("localhost:8080", logger)

network_info = subprocess.check_output(["ip", "address"], text=True)
logger.debug(f"Network status:\n{network_info}")

lcd = RGB1602(16,2)
lcd.setRGB(64, 128, 64)
lcd.print_line1(f"PTZ camera")

i2c = board.I2C()
aw9523 = adafruit_aw9523.AW9523(i2c)

preset_recall_button = IlluminatedButton(14, aw9523, 1)
preset_store_button  = IlluminatedButton(15, aw9523, 2)
zoom_in_button       = IlluminatedButton(18, aw9523, 3)
zoom_out_button      = IlluminatedButton(23, aw9523, 4)
focus_in_button      = IlluminatedButton(24, aw9523, 5)
focus_auto_button    = IlluminatedButton(25, aw9523, 6)
focus_out_button     = IlluminatedButton( 8, aw9523, 7)

quitter = Quitter(preset_recall_button, preset_store_button, lcd)
zoomer = Zoomer(zoom_in_button, zoom_out_button, camera, lcd)
focusser = Focusser(focus_in_button, focus_out_button, focus_auto_button, camera, lcd)

preset_recall_button.when_pressed = functools.partial(preset_recall, camera, lcd)
preset_store_button.when_pressed = functools.partial(preset_store, camera, lcd)

quitter.wait_for_exit()

logger.info("PTZ joystick camera stopping")