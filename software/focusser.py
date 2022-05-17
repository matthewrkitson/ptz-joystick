class Focusser():
    def __init__(self, focus_in_button, focus_out_button, focus_auto_button, camera, lcd):
        self.focus_in_button = focus_in_button
        self.focus_out_button = focus_out_button
        self.focus_auto_button = focus_auto_button
        self.camera = camera
        self.lcd = lcd

        self.focus_in_button.when_pressed = self.focus_in
        self.focus_in_button.when_released = self.focus_stop

        self.focus_out_button.when_pressed = self.focus_out
        self.focus_out_button.when_released = self.focus_stop

        self.focus_auto_button.when_pressed = self.focus_auto

    def focus_in(self):
        self.lcd.print_line1("Focus in")
        self.camera.focus_in(1)

    def focus_out(self):
        self.lcd.print_line1("Focus out")
        self.camera.focus_out(1)

    def focus_stop(self):
        self.lcd.print_line1("Focus stop")
        self.camera.focus_stop()

    def focus_auto(self):
        self.lcd.print_line1("Auto focus??")
        # self.camera.auto_focus()