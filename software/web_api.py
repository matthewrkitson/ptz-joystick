import requests

class WebApiController():
    def __init__(self, ip_address, logger):
        self.ip_address = ip_address

        self.logger = logger

        # Min and max values from PTZ camera documentation. 
        # docs/PTZOptics-HTTP-CGI-Commands-rev-1.4-1-20.pdf
        self.zoom_max = 7
        self.zoom_min = 1

    def _send_web_request(self, url):
        response = requests.get(url)
        self.logger.debug(f"{url} => {response.status_code}")
        response.raise_for_status()
        return response.content

    def zoom_in(self, speed):
        url = f"http://{self.ip_address}/cgi-bin/ptzctrl.cgi?ptzcmd&zoomin&{speed}"
        self._send_web_request(url)

    def zoom_out(self, speed):
        url = f"http://{self.ip_address}/cgi-bin/ptzctrl.cgi?ptzcmd&zoomout&{speed}"
        self._send_web_request(url)

    def zoom_stop(self):
        url = f"http://{self.ip_address}/cgi-bin/ptzctrl.cgi?ptzcmd&zoomstop"
        self._send_web_request(url)




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
