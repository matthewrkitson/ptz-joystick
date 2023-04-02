import datetime
import logging
import matplotlib.pyplot as plt
import matplotlib.animation
import threading
import time

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import visca

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

logger = logging.getLogger()


consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
logger.addHandler(consoleHandler)

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
consoleHandler.setFormatter(formatter)

logger.setLevel(logging.DEBUG)
logger.info("----------------------------")
logger.info(" Charts experiment starting ")
logger.info("----------------------------")

sys.excepthook = handle_exception
threading.excepthook = handle_exception


camera = visca.ViscaCamera("localhost", 5678, 1)

fig, ax = plt.subplots()
pan_data, tilt_data, zoom_data, times = [], [], [], []
pan_line, = ax.plot([], [], 'ro', label="pan")
tilt_line, = ax.plot([], [], 'bo', label="tilt")
zoom_line, = ax.plot([], [], 'go', label="zoom")

def recall_loop():
    camera.set_preset(0, 0xFAF0, 0x01B0, 0x0000)
    camera.set_preset(1, 0x0510, 0xFE50, 0x1000)
    camera.set_preset(2, 0x0510, 0x01B0, 0x0000)
    camera.set_preset(3, 0xFAF0, 0xFE50, 0x1000)

    while True:
        for p in range(3):
            camera.recall_preset(p)
            time.sleep(20)

def get_x_limits():
    x_min = (datetime.datetime.now() - datetime.timedelta(seconds=20)).timestamp()
    x_max = datetime.datetime.now().timestamp()
    return (x_min, x_max)   

def init():
    x_min, x_max = get_x_limits()
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-5000, 5000)
    ax.legend(loc="upper left")
    ax.set_title("Pan, tilt and zoom")
    return pan_line, tilt_line, zoom_line

def update(frame):
    global pan_data, tilt_data, zoom_data, times
    p, t, z = camera.ptz
    x_min, x_max = get_x_limits()
    times.append(datetime.datetime.now().timestamp())
    pan_data.append(p)
    tilt_data.append(t)
    zoom_data.append(z)

    times = [t for t in times if t > x_min]
    pan_data = pan_data[-len(times):]
    tilt_data = tilt_data[-len(times):]
    zoom_data = zoom_data[-len(times):]
    pan_line.set_data(times, pan_data)
    tilt_line.set_data(times, tilt_data)
    zoom_line.set_data(times, zoom_data)
    ax.set_xlim(x_min, x_max)
    return pan_line, tilt_line, zoom_line

ani = matplotlib.animation.FuncAnimation(fig, update, init_func=init, blit=True)

recall_thread = threading.Thread(target=recall_loop, daemon=True, group=None)
recall_thread.start()

plt.show()

