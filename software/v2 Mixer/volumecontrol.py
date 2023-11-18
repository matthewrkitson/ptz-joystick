import logging
import math
import threading
import time

import utils

class VolumeControl():
    def __init__(self, analogin, mixer, bus, invert=False):
        self.logger = logging.getLogger(__name__)
        self.analogin = analogin
        self.v_min = analogin.voltage_min
        self.v_max = analogin.voltage_max
        self.mixer = mixer
        self.f_min = mixer.fader_min
        self.f_max = mixer.fader_max
        if invert: (self.f_min, self.f_max) = (self.f_max, self.f_min)
        self.bus = bus

        try:    
            self.name = mixer.query(f"/bus/{self.bus:02d}/config/name")
        except:
            self.logger.exception("Unable to obtain bus name from mixer")
            self.name = "(unknown)"

        # Start a new thread to run the message loop
        self.finished = False;
        self.message_loop_thread = threading.Thread(target=self.message_loop, daemon=True)

    def start(self):
        self.message_loop_thread.start()

    def stop(self):
        self.logger.debug(f"{self.name}: Stopping volume control message loop")
        self.finished = True;
        self.message_loop_thread.join()
  
    def message_loop(self):
        self.logger.debug(f"{self.name}: Starting volume control meesage loop")
        last_value = math.inf
        current_value = 0
        delta = (self.v_max - self.v_min) / 500
        address = f"/bus/{self.bus:02d}/mix/fader"
        while not self.finished:
            try:
                current_value = self.analogin.voltage
                # self.logger.debug(f"Current value: {current_value} (last value: {last_value})")
                if abs(current_value - last_value) > delta:
                    fader_value = utils.interpolate(self.v_min, current_value, self.v_max, self.f_min, self.f_max)
                    # self.logger.debug(f"Setting {self.name} to {fader_value}")
                    self.mixer.send(address, fader_value)
                    last_value = current_value
            except: 
                self.logger.exception(f"Exception from {self.name} volume control")
                self.lcd.print_line1(f"Mixer error")
                self.lcd.print_line2(f"{self.name}")

            time.sleep(0.01)
        
        self.logger.debug(f"{self.name}: Finished volume control meessage loop")
