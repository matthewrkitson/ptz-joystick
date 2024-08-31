import logging
import time

import utils

class DigitalJoystick():
    def __init__(self, up_button, down_button, left_button, right_button, speed_value_provider, camera, lcd):
        self.up_button = up_button
        self.down_button = down_button
        self.left_button = left_button
        self.right_button = right_button
        self.speed_value_provider = speed_value_provider
        self.camera = camera
        self.lcd = lcd

        self.up_button.when_pressed = self.status_changed
        self.up_button.when_released = self.status_changed
        self.down_button.when_pressed = self.status_changed
        self.down_button.when_released = self.status_changed
        self.left_button.when_pressed = self.status_changed
        self.left_button.when_released = self.status_changed
        self.right_button.when_pressed = self.status_changed
        self.right_button.when_released = self.status_changed
        self.speed_value_provider.value_changed = self.status_changed

    def status_changed(self):
        speed = utils.interpolate(self.speed_value_provider.min, self.speed_value_provider.value, self.speed_value_provider.max, self.camera.pantilt_speed_min, self.camera.pantilt_speed_max, int)

        # It seems that the is_pressed property takes a moment to get updated,
        # so do a brief sleep here. 
        time.sleep(0.01)
        status = (self.up_button.is_pressed, self.down_button.is_pressed, self.left_button.is_pressed, self.right_button.is_pressed)
        logging.debug(f"Status changed: {status}")

        if status == (False, False, False, False):
            self.lcd.print_line1("Stop")
            self.lcd.print_line2("")
            self.camera.ptz_stop()
        elif status == (True, False, False, False):
            self.lcd.print_line1("Up")
            self.lcd.print_line2(f"Speed {speed}")
            self.camera.ptz_up(speed)
        elif status == (True, False, False, True):
            self.lcd.print_line1("Up, right")
            self.lcd.print_line2(f"Speed {speed}")
            self.camera.ptz_upright(speed)
        elif status == (False, False, False, True):
            self.lcd.print_line1("Right")
            self.lcd.print_line2(f"Speed {speed}")
            self.camera.ptz_right(speed)
        elif status == (False, True, False, True):
            self.lcd.print_line1("Down, right")
            self.lcd.print_line2(f"Speed {speed}")
            self.camera.ptz_downright(speed)
        elif status == (False, True, False, False):
            self.lcd.print_line1("Down")
            self.lcd.print_line2(f"Speed {speed}")
            self.camera.ptz_down(speed)
        elif status == (False, True, True, False):
            self.lcd.print_line1("Down, left")
            self.lcd.print_line2(f"Speed {speed}")
            self.camera.ptz_downleft(speed)
        elif status == (False, False, True, False):
            self.lcd.print_line1("Left")
            self.lcd.print_line2(f"Speed {speed}")
            self.camera.ptz_left(speed)
        elif status == (True, False, True, False):
            self.lcd.print_line1("Up, left")
            self.lcd.print_line2(f"Speed {speed}")
            self.camera.ptz_upleft(speed)
        else:
            self.lcd.print_line1(f"Unexpected")
            self.lcd.print_line2(f"direction")
            pass