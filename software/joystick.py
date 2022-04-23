import logging
import logging.handlers

import gpiozero
import signal

import web_api


logger = logging.getLogger(__name__)

fileHandler = logging.handlers.RotatingFileHandler("infopanel.log", maxBytes=1024*1024, backupCount=5)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
consoleHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)

logger.setLevel(logging.DEBUG)
logger.info("PTZ joystick controller starting")

controller = web_api.WebApiController("localhost:8080", logger)

zoom_in_button = gpiozero.Button(26)
zoom_out_button = gpiozero.Button(19)

zoom_in_button.when_pressed = lambda _: controller.zoom_in(1)
zoom_in_button.when_released = controller.zoom_stop

zoom_out_button.when_pressed = lambda _: controller.zoom_out(1)
zoom_out_button.when_released = controller.zoom_stop

signal.pause()

logger.info("PTZ joystick controller stopping")