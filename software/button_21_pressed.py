import gpiozero

button = gpiozero.Button(21)
if button.is_pressed:
    print("Button pressed")
    exit(0)
else:
    print("Button not pressed")
    exit(1)
