import functools
import gpiozero
import signal
import time

def button_pressed(index, button):
    print(f"Button {index} pressed.")

buttons = (
    gpiozero.Button(20),
    gpiozero.Button(21),
    gpiozero.Button(26),
    gpiozero.Button(19),
    gpiozero.Button(13),
    gpiozero.Button( 6),
    gpiozero.Button( 5),
)

for index, button in enumerate(buttons):
    button.when_pressed = functools.partial(button_pressed, index)

print("Press some buttons")

signal.pause()