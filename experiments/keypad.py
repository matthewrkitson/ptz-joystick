import gpiozero
import signal

col1 = gpiozero.LED(26)
col2 = gpiozero.LED(19)
col3 = gpiozero.LED(13)

row1 = gpiozero.Button(6)
row2 = gpiozero.Button(5)
row3 = gpiozero.Button(16)
row4 = gpiozero.Button(12)

columns = (col1, col2, col3)
rows = (row1, row2, row3, row4)

def column_pressed(column):
    print(f"Column pressed {column}")

for column in columns:
    column.when_pressed = column_pressed