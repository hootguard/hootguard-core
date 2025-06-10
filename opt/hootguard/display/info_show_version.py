# Script Name: info_show_version.py
# Version: 0.2
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script displays the current version of the HootGuard system on an I2C-connected LCD screen.
# Reads the version information from a file dynamically specified in the global configuration.

import sys
from RPLCD.i2c import CharLCD
from display_lock import display_lock

# Add the path to global_config_loader.py
sys.path.append('/opt/hootguard/main/scripts')
from global_config_loader import load_config  # Import load_config function

# Load the global configuration
config = load_config()
VERSION_FILE_PATH = config['misc']['version_file']

# Initialize the LCD
I2C_ADDR = 0x27

lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDR, port=3,
              cols=16, rows=2, dotsize=8,
              charmap='A02',
              auto_linebreaks=True,
              backlight_enabled=True)

def get_version():
    try:
        with open(VERSION_FILE_PATH, 'r') as file:
            version = file.read().strip()
            return version
    except Exception as e:
        return "Error reading snooze time"

def main():
    with display_lock:
        version = get_version()
        lcd.clear()
        lcd.write_string("Version")
        lcd.crlf()
        lcd.write_string(version)

if __name__ == "__main__":
    main()
