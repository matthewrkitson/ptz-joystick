import functools
import gpiozero
import signal
import time

def button_pressed(direction, button):
    print(f"Joystick moved {direction}")

up    = gpiozero.Button(14)
down  = gpiozero.Button(15)
left  = gpiozero.Button(18)
right = gpiozero.Button(23)

up.when_pressed = functools.partial(button_pressed, "up")
down.when_pressed = functools.partial(button_pressed, "down")
left.when_pressed = functools.partial(button_pressed, "left")
right.when_pressed = functools.partial(button_pressed, "right")

print("Move the arcade joystick")

signal.pause()