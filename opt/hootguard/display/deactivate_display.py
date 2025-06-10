# Script Name: deactivate_display.py
# Version: 0.2
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script deactivates an I2C-connected LCD display by clearing the screen and turning off the backlight.
# - Uses the RPLCD library to interface with the LCD.
# - Locks the display using `display_lock` to ensure thread-safe access.
# - Clears the display content and disables the backlight.
# Intended for use in the HootGuard system to power down the display when not needed.


from RPLCD.i2c import CharLCD
from display_lock import display_lock

I2C_ADDR = 0x27

lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDR, port=3,
              cols=16, rows=2, dotsize=8,
              charmap='A02',
              auto_linebreaks=True,
              backlight_enabled=True)

def main():
    with display_lock:
        lcd.clear()
        lcd.backlight_enabled = False

if __name__ == "__main__":
    main()
