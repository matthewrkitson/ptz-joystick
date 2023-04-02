class Zoomer():
    def __init__(self, zoom_in_button, zoom_out_button, camera, lcd):
        self.zoom_in_button = zoom_in_button
        self.zoom_out_button = zoom_out_button
        self.camera = camera
        self.lcd = lcd

        self.zoom_in_button.when_pressed = self.zoom_in
        self.zoom_in_button.when_released = self.zoom_stop

        self.zoom_out_button.when_pressed = self.zoom_out
        self.zoom_out_button.when_released = self.zoom_stop

    def zoom_in(self):
        self.lcd.print_line1("Zoom in")
        self.camera.zoom_in(1)

    def zoom_out(self):
        self.lcd.print_line1("Zoom out")
        self.camera.zoom_out(1)

    def zoom_stop(self):
        self.lcd.print_line1("Zoom stop")
        self.camera.zoom_stop()
