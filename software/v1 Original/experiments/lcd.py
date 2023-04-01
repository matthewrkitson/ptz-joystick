import lcd1602rgb
import signal
import subprocess

lcd=lcd1602rgb.RGB1602(16,2)

lcd.setRGB(64, 128, 64);


hostname_result = subprocess.check_output(["hostname", "-I"], text=True)
addresses = hostname_result.split()

if len(addresses) > 0:
    lcd.setCursor(0, 0)
    lcd.printout(f"{addresses[0]}")

if len(addresses) > 1:
    lcd.setCursor(0, 1)
    lcd.printout(f"{addresses[1]}")

signal.pause()