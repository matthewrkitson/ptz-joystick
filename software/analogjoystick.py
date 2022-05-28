import logging
import threading
import time

import donotrepeat
import utils

class AnalogJoystick():
    def __init__(self, updown, leftright, camera, lcd):
        self.updown = updown
        self.leftright = leftright
        self.camera = camera
        self.lcd = lcd

        # Assume joystick is central when creating controller. 
        self.leftright_centre = self.leftright.voltage
        self.updown_centre = self.updown.voltage

        # Start a new thread to run the message loop
        self.message_loop_thread = threading.Thread(target=self.message_loop, daemon=True)
        self.message_loop_thread.start()

    def interpolate(self, value):
        return utils.interpolate(0, self.leftright.voltage, 3.3, self.camera.pantilt_min, self.camera.pantilt_max)
  
    def message_loop(self):
        dnr = donotrepeat.DoNotRepeat()
        while True:
            try:
                speed_left = None
                speed_right = None
                speed_up = None
                speed_down = None
                stop_buffer = 2

                left_v = self.leftright_centre - self.leftright.voltage
                if left_v > 0:
                    speed_left = utils.interpolate(self.leftright_centre, self.leftright.voltage, 0, self.camera.pan_speed_min - stop_buffer, self.camera.pan_speed_max)
                    if speed_left < self.camera.pan_speed_min: speed_left = None

                right_v = self.leftright.voltage - self.leftright_centre
                if right_v > 0:
                    speed_right = utils.interpolate(self.leftright_centre, self.leftright.voltage, 3.3, self.camera.pan_speed_min - stop_buffer, self.camera.pan_speed_max)
                    if speed_right < self.camera.pan_speed_min: speed_right = None

                up_v = self.updown.voltage - self.updown_centre
                if up_v > 0:
                    speed_up = utils.interpolate(self.updown_centre, self.updown.voltage, 3.3, self.camera.tilt_speed_min - stop_buffer, self.camera.tilt_speed_max)
                    if speed_up < self.camera.tilt_speed_min: speed_up = None

                down_v = self.updown_centre - self.updown.voltage
                if down_v > 0:
                    speed_down = utils.interpolate(self.updown_centre, self.updown.voltage, 0, self.camera.tilt_speed_min - stop_buffer, self.camera.tilt_speed_max)
                    if speed_down < self.camera.tilt_speed_min: speed_down = None

                if not speed_up and not speed_down and not speed_left and not speed_right:
                    if dnr.do_not_repeat("stop"):
                        self.camera.ptz_stop()
                        self.lcd.print_line1("Stop")
                        self.lcd.print_line2(f"")
                elif speed_up and not speed_down and not speed_left and not speed_right:
                    if dnr.do_not_repeat(f"up-{speed_up}"):
                        self.camera.ptz_up(speed_up)
                        self.lcd.print_line1("Up")
                        self.lcd.print_line2(f"Speed: {speed_up}")
                elif speed_up and not speed_down and not speed_left and speed_right:
                    if dnr.do_not_repeat(f"up-right-{speed_right}-{speed_up}"):
                        self.camera.ptz_upright(speed_right, speed_up)
                        self.lcd.print_line1("Up-right")
                        self.lcd.print_line2(f"Speed: {speed_right}, {speed_up}")
                elif not speed_up and not speed_down and not speed_left and speed_right:
                    if dnr.do_not_repeat(f"right-{speed_right}"):
                        self.camera.ptz_right(speed_right)
                        self.lcd.print_line1("Right")
                        self.lcd.print_line2(f"Speed: {speed_right}")
                elif not speed_up and speed_down and not speed_left and speed_right:
                    if dnr.do_not_repeat(f"down-right-{speed_right}-{speed_down}"):
                        self.camera.ptz_downright(speed_right, speed_down)
                        self.lcd.print_line1("Down-right")
                        self.lcd.print_line2(f"Speed: {speed_right}, {speed_down}")
                elif not speed_up and speed_down and not speed_left and not speed_right:
                    if dnr.do_not_repeat(f"down-{speed_down}"):
                        self.camera.ptz_down(speed_down)
                        self.lcd.print_line1("Down")
                        self.lcd.print_line2(f"Speed: {speed_down}")
                elif not speed_up and speed_down and speed_left and not speed_right:
                    if dnr.do_not_repeat(f"down-left-{speed_left}-{speed_down}"):
                        self.camera.ptz_downleft(speed_left, speed_down)
                        self.lcd.print_line1("Down-left")
                        self.lcd.print_line2(f"Speed: {speed_left}, {speed_down}")
                elif not speed_up and not speed_down and speed_left and not speed_right:
                    if dnr.do_not_repeat(f"left-{speed_left}"):
                        self.camera.ptz_left(speed_left)
                        self.lcd.print_line1("Left")
                        self.lcd.print_line2(f"Speed: {speed_left}")
                elif speed_up and not speed_down and speed_left and not speed_right:
                    if dnr.do_not_repeat(f"up-left-{speed_left}-{speed_up}"):
                        self.camera.ptz_upleft(speed_left, speed_up)
                        self.lcd.print_line1("Up-left")
                        self.lcd.print_line2(f"Speed: {speed_left}, {speed_up}")
                else:
                    if dnr.do_not_repeat(f"unexpected"):
                        logging.warning(f"Unexpected combination of speeds for analogue joystick: up: {speed_up}, down: {speed_down}, left: {speed_left}, right: {speed_right}.")
                        self.lcd.print_line1("Unexpected dir.")
                        self.lcd.print_line2(f"UDLR: {speed_up}, {speed_down}, {speed_left}, {speed_right}")

            except: 
                if dnr.do_not_repeat(f"exception"):
                    logging.exception("Exception from analog joystick")

            time.sleep(0.1)
