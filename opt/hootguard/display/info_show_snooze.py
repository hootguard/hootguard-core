# Script Name: info_show_snooze.py
# Version: 0.1
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script displays the remaining snooze time on an I2C-connected LCD screen.
# - Reads the snooze time (in seconds) from a file located at `/opt/hootguard/snooze/snooze-time.txt`.
# - Converts the snooze time into a human-readable format (minutes and seconds).
# - If the file cannot be read or an error occurs, displays "Error reading snooze time."
# - Ensures thread-safe access to the display using `display_lock`.
# - Clears the screen and displays the snooze time with the label "Snooze Time."
# Designed for use in the HootGuard system to provide snooze status on the display.

import sys
import os
from RPLCD.i2c import CharLCD
from display_lock import display_lock

# Add the path to global_config_loader.py
sys.path.append('/opt/hootguard/main/scripts')
from global_config_loader import load_config  # Import load_config function

# Load the global configuration
config = load_config()

SNOOZE_TIME_FILE_PATH = config['misc']['snooze_time_file']

# Initialize the LCD
I2C_ADDR = 0x27

lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDR, port=3,
              cols=16, rows=2, dotsize=8,
              charmap='A02',
              auto_linebreaks=True,
              backlight_enabled=True)

def get_snooze_time():
    try:
        #with open('/opt/hootguard/snooze/snooze-time.txt', 'r') as file:
        with open(SNOOZE_TIME_FILE_PATH, 'r') as file:
            snooze_seconds = int(file.read().strip())
            minutes = snooze_seconds // 60
            seconds = snooze_seconds % 60
            return f"{minutes} min {seconds} sec"
    except Exception as e:
        return "Error reading snooze time"

def main():
    with display_lock:
        snooze_time = get_snooze_time()
        lcd.clear()
        lcd.write_string("Snooze Time")
        lcd.crlf()
        lcd.write_string(snooze_time)

if __name__ == "__main__":
    main()
