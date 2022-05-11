import functools
import gpiozero
import logging
import logging.handlers
import subprocess

from illuminatedbutton import IlluminatedButton
from lcd1602rgb import RGB1602
from quitter import Quitter

import web_api

def preset_recall(controller, lcd):
    lcd.print_line1("Preset recall")

def preset_store(controller, lcd):
    lcd.print_line1("Preset store")

def zoom_in(controller, lcd):
    lcd.print_line1("Zoom in")

def zoom_out(controller, lcd):
    lcd.print_line1("Zoom out")

def focus_in(controller, lcd):
    lcd.print_line1("Focus in")

def focus_out(controller, lcd):
    lcd.print_line1("Focus out")

def focus_auto(controller, lcd):
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
logger.info("PTZ joystick controller starting")

controller = web_api.WebApiController("localhost:8080", logger)

network_info = subprocess.check_output(["ip", "address"], text=True)
logger.debug(f"Network status:\n{network_info}")

lcd = RGB1602(16,2)
lcd.setRGB(64, 128, 64)
lcd.print_line1(f"PTZ Controller")

preset_recall_button = IlluminatedButton(14,    7)
preset_store_button  = IlluminatedButton(15,   12)
zoom_in_button       = IlluminatedButton(18,   16)
zoom_out_button      = IlluminatedButton(23,   26)
focus_in_button      = IlluminatedButton(24, None)
focus_auto_button    = IlluminatedButton(25, None)
focus_out_button     = IlluminatedButton( 8, None)

quitter = Quitter(preset_recall_button, preset_store_button, lcd)

preset_recall_button.when_pressed = functools.partial(preset_recall, controller, lcd)
preset_store_button.when_pressed = functools.partial(preset_store, controller, lcd)

zoom_in_button.when_pressed = functools.partial(zoom_in, controller, lcd)
zoom_out_button.when_pressed = functools.partial(zoom_out, controller, lcd)

focus_in_button.when_pressed = functools.partial(focus_in, controller, lcd)
focus_out_button.when_pressed = functools.partial(focus_out, controller, lcd)
focus_auto_button.when_pressed = functools.partial(focus_auto, controller, lcd)

quitter.wait_for_exit()

logger.info("PTZ joystick controller stopping")