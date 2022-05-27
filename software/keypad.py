import functools
import gpiozero
import logging

class Keypad():
    def __init__(self, col_pins, row_pins):
        if len(col_pins) != 3:
            raise ValueError("You must specify exactly three column pins")

        if len(row_pins) != 4:
            raise ValueError("You must specify exactly four row pins")
        
        col1 = gpiozero.LED(col_pins[0])
        col2 = gpiozero.LED(col_pins[1])
        col3 = gpiozero.LED(col_pins[2])
        
        # Columns should be connected to Vcc, not ground. 
        row1 = gpiozero.Button(row_pins[0], pull_up=False)
        row2 = gpiozero.Button(row_pins[1], pull_up=False)
        row3 = gpiozero.Button(row_pins[2], pull_up=False)
        row4 = gpiozero.Button(row_pins[3], pull_up=False)

        self.keypress_handler = None
        
        self.columns = (col1, col2, col3)
        self.rows = (row1, row2, row3, row4)
        self.keys = (
            ( 1,  2,  3),
            ( 4,  5,  6),
            ( 7,  8,  9),
            ("*", 0, "#")
        )
    
        for column in self.columns:
            column.on()
        
        for index, row in enumerate(self.rows):
            row.when_pressed = functools.partial(self.row_pressed, index)
  
    def button_pressed(self, row_index, column_index):
        key = self.keys[row_index][column_index]
        logging.debug(f"Keypad button pressed: {key} ({column_index}, {row_index})")
        if self.keypress_handler:
            self.keypress_handler(key)
  
    def row_pressed(self, row_index, row):
        if not row.is_active: return
    
        for column_index, column in enumerate(self.columns):
            column.off()
            if not row.is_active:
                self.button_pressed(row_index, column_index)
            column.on()
    
  