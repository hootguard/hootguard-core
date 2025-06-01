# Script Name: info_show_ip.py
# Version: 0.3
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script displays the system's current IP address on an I2C-connected LCD screen.
# - Retrieves the IP address of the system by connecting to a public DNS server (8.8.8.8).
# - If unable to fetch the IP, displays "No IP found" on the LCD.
# - Ensures thread-safe access to the display using `display_lock`.
# - Clears the screen and writes the IP address along with the label "IP Address."
# Designed for use in the HootGuard system as part of its display functionality.

import socket
from RPLCD.i2c import CharLCD
from display_lock import display_lock

I2C_ADDR = 0x27

lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDR, port=3,
              cols=16, rows=2, dotsize=8,
              charmap='A02',
              auto_linebreaks=True,
              backlight_enabled=True)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "No IP found"
    finally:
        s.close()
    return ip

def main():
    with display_lock:
        ip_address = get_ip_address()
        lcd.clear()
        lcd.write_string("IP Address")
        lcd.crlf()
        lcd.write_string(ip_address)

if __name__ == "__main__":
    main()
