# Script Name: welcome_display.py
# Version: 0.2
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script displays a welcome message on an I2C-connected LCD screen for the HootGuard system.
# - Initializes the LCD display with a backlight enabled.
# - Centers and displays the text "Welcome to" on the first line and "HootGuard" on the second line.
# - Keeps the message visible for 10 seconds before clearing the screen and turning off the backlight.
# Includes a utility function `center_text` to align text for optimal readability.
# Designed to provide a startup greeting on the HootGuard system's LCD display.

from RPLCD.i2c import CharLCD
from time import sleep

# Define the I2C address (replace with your detected address)
I2C_ADDR = 0x27

# Initialize the LCD on bus 3
lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDR, port=3,  # Change port to 3
              cols=16, rows=2, dotsize=8,
              charmap='A02',
              auto_linebreaks=True,
              backlight_enabled=True)  # Enable backlight initially

def center_text(text, width):
    if len(text) < width:
        padding = (width - len(text)) // 2
        return ' ' * padding + text
    else:
        return text

def main():
    lcd.clear()
    line1 = center_text("Welcome to", 16)
    line2 = center_text("HootGuard", 16)
    lcd.write_string(line1)
    lcd.crlf()  # Move to the second line
    lcd.write_string(line2)
    sleep(10)
    lcd.clear()
    lcd.backlight_enabled = False

if __name__ == "__main__":
    main()
