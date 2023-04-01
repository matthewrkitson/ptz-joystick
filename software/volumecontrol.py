import logging
import math
import threading
import time

import utils

class VolumeControl():
    def __init__(self, analogin, mixer, bus, lcd):
        self.analogin = analogin
        self.mixer = mixer
        self.bus = bus
        self.lcd = lcd

        try:    
            self.name = mixer.query(f"/bus/{self.bus:02d}/config/name")
        except:
            logging.exception("Unable to obtain bus name from mixer")
            self.name = "(unknown)"

        # Start a new thread to run the message loop
        self.finished = False;
        self.message_loop_thread = threading.Thread(target=self.message_loop, daemon=True)

    def start(self):
        self.message_loop_thread.start()

    def stop(self):
        logging.debug(f"{self.name}: Stopping volume control message loop")
        self.finished = True;
        self.message_loop_thread.join()
  
    def message_loop(self):
        logging.debug(f"{self.name}: Starting volume control meesage loop")
        last_value = math.inf
        current_value = 0
        address = f"/bus/{self.bus:02d}/mix/fader"
        while not self.finished:
            try:
                current_value = self.analogin.voltage
                if abs(current_value - last_value) > 0.01:
                    fader_value = utils.interpolate(self.analogin.voltage_min, current_value, self.analogin.voltage_max, self.mixer.fader_min, self.mixer.fader_max)
                    logging.debug(f"Setting {self.name} to {fader_value}")
                    self.mixer.send(address, fader_value)
            except: 
                logging.exception(f"Exception from {self.name} volume control")
                self.lcd.print_line1(f"Mixer error")
                self.lcd.print_line2(f"{self.name}")
            finally:
                last_value = current_value

            time.sleep(0.01)
        
        logging.debug(f"{self.name}: Finished volume control meessage loop")
