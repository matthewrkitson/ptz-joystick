import requests

import utils

class WebApiController():
    def __init__(self, ip_address, logger):
        self.ip_address = ip_address

        self.logger = logger

        # Min and max values from PTZ camera documentation. 
        # docs/PTZOptics-HTTP-CGI-Commands-rev-1.4-1-20.pdf
        self.zoom_speed_max = 7
        self.zoom_speed_min = 1
        self.focus_speed_max = 7
        self.focus_speed_min = 1
        self.pan_speed_min = 1
        self.pan_speed_max = 24
        self.tilt_speed_min = 1
        self.tilt_speed_max = 20
        self.pantilt_speed_min = max(self.pan_speed_min, self.tilt_speed_min)
        self.pantilt_speed_max = min(self.pan_speed_max, self.tilt_speed_max)

    def _send_web_request(self, url):
        pass
        response = requests.get(url)
        self.logger.debug(f"{url} => {response.status_code}")
        response.raise_for_status()
        return response.content

    def zoom_in(self, speed):
        speed = utils.clamp(speed, self.zoom_speed_min, self.zoom_speed_max)
        url = f"http://{self.ip_address}/cgi-bin/ptzctrl.cgi?ptzcmd&zoomin&{speed}"
        self._send_web_request(url)

    def zoom_out(self, speed):
        speed = utils.clamp(speed, self.zoom_speed_min, self.zoom_speed_max)
        url = f"http://{self.ip_address}/cgi-bin/ptzctrl.cgi?ptzcmd&zoomout&{speed}"
        self._send_web_request(url)

    def zoom_stop(self):
        url = f"http://{self.ip_address}/cgi-bin/ptzctrl.cgi?ptzcmd&zoomstop"
        self._send_web_request(url)

    def focus_in(self, speed):
        speed = utils.clamp(speed, self.focus_speed_min, self.focus_speed_max)
        url = f"http://{self.ip_address}/cgi-bin/ptzctrl.cgi?ptzcmd&focusin&{speed}"
        self._send_web_request(url)

    def focus_out(self, speed):
        speed = utils.clamp(speed, self.focus_speed_min, self.focus_speed_max)
        url = f"http://{self.ip_address}/cgi-bin/ptzctrl.cgi?ptzcmd&focusout&{speed}"
        self._send_web_request(url)

    def focus_stop(self):
        url = f"http://{self.ip_address}/cgi-bin/ptzctrl.cgi?ptzcmd&focusstop"
        self._send_web_request(url)

    def focus_lock(self):
        url = f"http://{self.ip_address}/cgi-bin/ptzctrl.cgi?ptzcmd&lock_mfocus"
        self._send_web_request(url)

    def focus_unlock(self):
        url = f"http://{self.ip_address}/cgi-bin/ptzctrl.cgi?ptzcmd&unlock_mfocus"
        self._send_web_request(url)

    def _ptz_go(self, direction, pan_speed, tilt_speed=None):
        if tilt_speed == None: tilt_speed = pan_speed
        pan_speed = utils.clamp(pan_speed, self.pan_speed_min, self.pan_speed_max, True)
        tilt_speed = utils.clamp(tilt_speed, self.tilt_speed_min, self.tilt_speed_max, True)
        url = f"http://{self.ip_address}/cgi-bin/ptzctrl.cgi?ptzcmd&{direction}&{pan_speed}&{tilt_speed}"
        # self._send_web_request(url)

    def ptz_stop(self):
        self._ptz_go("ptzstop", self.pan_speed_min, self.tilt_speed_min)

    def ptz_up(self, pan_speed, tilt_speed=None):
        self._ptz_go("up", pan_speed, tilt_speed)

    def ptz_upright(self, pan_speed, tilt_speed=None):
        self._ptz_go("rightup", pan_speed, tilt_speed)

    def ptz_right(self, pan_speed, tilt_speed=None):
        self._ptz_go("right", pan_speed, tilt_speed)

    def ptz_downright(self, pan_speed, tilt_speed=None):
        self._ptz_go("rightdown", pan_speed, tilt_speed)

    def ptz_down(self, pan_speed, tilt_speed=None):
        self._ptz_go("down", pan_speed, tilt_speed)

    def ptz_downleft(self, pan_speed, tilt_speed=None):
        self._ptz_go("leftdown", pan_speed, tilt_speed)

    def ptz_left(self, pan_speed, tilt_speed=None):
        self._ptz_go("left", pan_speed, tilt_speed)

    def ptz_upleft(self, pan_speed, tilt_speed=None):
        self._ptz_go("leftup", pan_speed, tilt_speed)


    #
    # Web API:
    # 
    # base url: http://camera_address/cgi-bin/ptzctrl.cgi?ptzcmd&COMMAND&OPTION1&OPTION2...
    #
    # 
    # zoomin SPEED
    # zoomout SPEED
    # zoomstop
    # zoomto SPEED POSITION
    #
    #   SPEED in range [0, 7]
    #   POSITION is hex value in range [0x0000, 0x4000]
    #   zoomin and zoomout keep going until zoomstop is received

    # home
    # Resets to home position
    # 
    # http://camera_address/snapshot.jpg
    # Downloads a JPEG image (note that the filename is imoprtant; it must be snapshot.jpg)
    #
    #
