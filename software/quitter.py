import functools
import subprocess
import threading

class Quitter():
    def __init__(self, preset_recall_button, preset_store_button, lcd):
        self.lcd = lcd
        self.exit_event = threading.Event()
        self.preset_recall_button = preset_recall_button
        self.preset_store_button = preset_store_button

        # Add ability to reboot and turn off.
        # Also hidden ability to terminate app before doing interactive development
        # (as the app gets started when the device boots)
        self.preset_recall_button.hold_time = 5
        self.preset_store_button.hold_time = 5
        self.preset_recall_button.when_held = self.preset_recall_button_held
        self.preset_store_button.when_held = self.preset_store_button_held

    def preset_recall_button_held(self):
        if self.preset_store_button.is_pressed:
            self.terminate_app()
        else:
            self.reboot()

    def preset_store_button_held(self):
        if self.preset_recall_button.is_pressed:
            self.terminate_app()
        else:
            self.poweroff()

    def terminate_app(self):
        self.lcd.print_line1(f"Exit")
        self.exit_event.set()

    def reboot(self):
        self.lcd.print_line1(f"Reboot...")
        subprocess.run(["sudo", "reboot"])

    def poweroff(self):
        self.lcd.print_line1(f"Power off...")
        subprocess.run(["sudo", "poweroff"])

    def wait_for_exit(self):
        self.exit_event.wait()