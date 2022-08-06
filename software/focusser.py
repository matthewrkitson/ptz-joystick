class Focusser():
    def __init__(self, focus_in_button, focus_out_button, focus_lock_button, camera, lcd):
        self.focus_in_button = focus_in_button
        self.focus_out_button = focus_out_button
        self.focus_lock_button = focus_lock_button
        self.camera = camera
        self.lcd = lcd

        self.focus_in_button.when_pressed = self.focus_in
        self.focus_in_button.when_released = self.focus_stop

        self.focus_out_button.when_pressed = self.focus_out
        self.focus_out_button.when_released = self.focus_stop

        self.focus_lock_button.when_pressed = self.focus_lock_toggle

    def focus_in(self):
        self.lcd.print_line1("Focus in")
        self.camera.focus_in(1)

    def focus_out(self):
        self.lcd.print_line1("Focus out")
        self.camera.focus_out(1)

    def focus_stop(self):
        self.lcd.print_line1("Focus stop")
        self.camera.focus_stop()

    def focus_lock_toggle(self):
        if self.camera.focus_locked:
            self.camera.focus_unlock()
            self.lcd.print_line1("Focus lock off")
        else:
            self.camera.focus_lock()
            self.lcd.print_line1("Focus lock on")