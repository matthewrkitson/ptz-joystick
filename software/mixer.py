import logging
import xair_api

class Mixer:
    def __init__(self, kind, ip):
        try:
            self.mixer = xair_api.connect(kind, ip=ip)
            self.mixer.validate_connection()
            logging.debug(f"Created mixer: {self.mixer}")
        except:
            logging.exception(f"Unable to create mixer of type {kind} at {ip}")
            self.mixer = None

    fader_max = 1
    fader_min = 0

    values = {
        "/bus/09/config/name": "Desk to PC",
        "/bus/10/config/name": "iPad to PC"
    }

    def query(self, address):
        if not self.mixer: 
            value = self.values[address] if address in self.values else None
            logging.debug(f"No mixer; unable to query {address}, using dummy value '{value}'")
            return value

        try:
            return self.mixer.query(address)
        except:
            logging.exception(f"Exception when querying {address}")
            return None

    def send(self, address, value):
        if not self.mixer:
            logging.debug(f"No mixer; unable to send {value} to {address}")
            return

        try:
            self.mixer.send(address, value)
        except:
            logging.exception(f"Exception when sending {value} to {address}")