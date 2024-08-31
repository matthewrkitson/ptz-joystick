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
logger.info("PTZ camera joystick starting")
logger.info("----------------------------")

sys.excepthook = handle_exception
threading.excepthook = handle_exception


network_info = subprocess.check_output(["ip", "address"], text=True)
logging.info(f"Network status:\n{network_info}")

i2c_lock = threading.Lock()

lcd = RGB1602(col=16, row=2, i2c_lock=i2c_lock)
lcd.setRGB(64, 128, 64)
lcd.print_line1(f"PTZ camera")

i2c = board.I2C()
aw9523 = adafruit_aw9523.AW9523(i2c)

rotary1_int_pin = gpiozero.Button(25, pull_up=None, active_state=False)
rotary1_seesaw = adafruit_seesaw.seesaw.Seesaw(board.I2C(), 0x36)

# ads1015 = adafruit_ads1x15.ads1015.ADS1015(i2c)
# analog_joystick_horizontal = AnalogIn(ads1015, AnalogIn.P0, i2c_lock)
# speed_dial = AnalogIn(ads1015, AnalogIn.P1, i2c_lock)
# analog_joystick_vertical = AnalogIn(ads1015, AnalogIn.P2, i2c_lock)
# speed_slider = AnalogIn(ads1015, AnalogIn.P3, i2c_lock)
# speed_value_provider = AnalogValueProvider(...)

preset_recall_button = IlluminatedButton(20, aw9523, 1, i2c_lock)
preset_store_button  = IlluminatedButton(21, aw9523, 2, i2c_lock)
zoom_in_button       = IlluminatedButton(26, aw9523, 3, i2c_lock)
zoom_out_button      = IlluminatedButton(19, aw9523, 4, i2c_lock)
focus_in_button      = IlluminatedButton(13, aw9523, 5, i2c_lock)
focus_lock_button    = IlluminatedButton( 6, aw9523, 6, i2c_lock)
focus_out_button     = IlluminatedButton( 5, aw9523, 7, i2c_lock)

# camera = web_api.WebApiController("localhost:8080", focus_lock_button)
camera = web_api.WebApiController("192.168.56.174", focus_lock_button)

speed_value_provider = RotaryValueProvider(camera.pantilt_speed_min, camera.pantilt_speed_max, "Speed", rotary1_seesaw, rotary1_int_pin, lcd)

joystick_up_button    = gpiozero.Button(14)
joystick_down_button  = gpiozero.Button(15)
joystick_left_button  = gpiozero.Button(18)
joystick_right_button = gpiozero.Button(23)

keypad = Keypad((4, 17, 27), (22, 10, 9, 11))

quitter = Quitter(preset_recall_button, preset_store_button, lcd)
zoomer = Zoomer(zoom_in_button, zoom_out_button, camera, lcd)
focusser = Focusser(focus_in_button, focus_out_button, focus_lock_button, camera, lcd)
digital_joystick = DigitalJoystick(joystick_up_button, joystick_down_button, joystick_left_button, joystick_right_button, speed_value_provider, camera, lcd)
# analog_joystick = AnalogJoystick(analog_joystick_vertical, analog_joystick_horizontal, camera, lcd)
recaller = Recaller(keypad, preset_recall_button, preset_store_button, camera, lcd)

logger.info("PTZ camera joystick active")
# analog_joystick.message_loop()

quitter.wait_for_exit()

logger.info("PTZ camera joystick stopping")
