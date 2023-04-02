import datetime
import time
import math
import matplotlib.pyplot as plt
import matplotlib.animation
import matplotlib.ticker as mticks

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import visca

camera = visca.ViscaCamera("localhost", 5678, 1)

fig, ax = plt.subplots()
pan_data, tilt_data, zoom_data, times = [], [], [], []
pan_line, = ax.plot([], [], 'ro', label="pan")
tilt_line, = ax.plot([], [], 'bo', label="tilt")
zoom_line, = ax.plot([], [], 'go', label="zoom")

def get_x_limits():
    x_min = (datetime.datetime.now() - datetime.timedelta(seconds=20)).timestamp()
    x_max = datetime.datetime.now().timestamp()
    return (x_min, x_max)   

def init():
    x_min, x_max = get_x_limits()
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-3000, 3000)
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
plt.show()

