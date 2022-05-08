import functools
import gpiozero
import signal

col1 = gpiozero.LED(19)
col2 = gpiozero.LED(13)
col3 = gpiozero.LED( 6)

row1 = gpiozero.Button( 5,  pull_up=False)
row2 = gpiozero.Button(11,  pull_up=False)
row3 = gpiozero.Button( 9, pull_up=False)
row4 = gpiozero.Button(10, pull_up=False)

columns = (col1, col2, col3)
rows = (row1, row2, row3, row4)
keys = (
    ( 1,  2,  3),
    ( 4,  5,  6),
    ( 7,  8,  9),
    ("*", 0, "#")
)

def button_pressed(row_index, column_index):
    print(f"{keys[row_index][column_index]} ({column_index}, {row_index})")

def row_pressed(row_index, row):
    if not row.is_active: return

    for column_index, column in enumerate(columns):
        column.off()
        if not row.is_active:
            button_pressed(row_index, column_index)
        column.on()

for column in columns:
    column.on()

for index, row in enumerate(rows):
    row.when_pressed = functools.partial(row_pressed, index)

signal.pause()