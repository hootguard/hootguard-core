# Script Name: snooze_activate.py
# Version: 0.2
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script activates the snooze functionality on the HootGuard system.
# It interacts with Pi-hole to temporarily disable it, controls an LED indicator,
# and displays the snooze time on an I2C-connected LCD screen.

import sys
import os
from RPLCD.i2c import CharLCD
from display_lock import display_lock
import threading
import RPi.GPIO as GPIO
import time
import requests
import subprocess

# Add the path to global_config_loader.py
sys.path.append('/opt/hootguard/main/scripts')

from global_config_loader import load_config  # Import load_config function

# Load the global configuration
config = load_config()
TIMER_FILE = config['misc']['snooze_time_file']
STATUS_FILE = config['misc']['snooze_status_file']

# Initialize the LCD
I2C_ADDR = 0x27

lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDR, port=3,
              cols=16, rows=2, dotsize=8,
              charmap='A02', auto_linebreaks=True,
              backlight_enabled=True)  # Enable backlight initially

with display_lock:
    lcd.clear()
    lcd.write_string("Snooze active")

# GPIO setup for the LED and button
LED_PIN = 16  # GPIO pin for the LED
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.HIGH)

# Snooze timer - File to store and read snooze time
#TIMER_FILE = '/opt/hootguard/snooze/snooze-time.txt'
#STATUS_FILE = '/opt/hootguard/snooze/snooze-status.txt'

def get_local_ip_address():
    """Get the current local IP address of the Raspberry Pi."""
    try:
        # Use hostname command to get the IP address
        ip_address = subprocess.check_output(['hostname', '-I']).decode().strip().split(' ')[0]
        return ip_address
    except Exception as e:
        print(f"Error obtaining local IP: {e}")
        return "127.0.0.1"

PIHOLE_IP = get_local_ip_address()  # Get and store the local IP address of the Pi

def get_webpassword():
    """Get the current web password for Pi-hole from the system configuration file."""
    try:
        # Use shell command to read the Pi-hole webpassword from setupVars.conf
        output = subprocess.check_output("cat /etc/pihole/setupVars.conf | grep WEBPASSWORD", shell=True).decode().strip()
        webpassword = output.split('=')[1]  # Extract the password from the output
        return webpassword
    except Exception as e:
        print(f"Error obtaining web password: {e}")
        return None

def get_snooze_time():
    """Read the snooze time setting from a file."""
    try:
        with open(TIMER_FILE, 'r') as file:
            return file.read().strip()  # Read and return the snooze time
    except FileNotFoundError:
        return "300"  # Return default value if file not found

def deactivate_pihole():
    """Deactivate the Pi-hole for a set duration."""
    auth = get_webpassword()  # Retrieve the current web password
    if not auth:
        print("Failed to retrieve web password. Cannot deactivate Pi-hole.")
        return

    snooze_time = get_snooze_time()  # Get the snooze time
    url = f"http://{PIHOLE_IP}/admin/api.php?disable={snooze_time}&auth={auth}"  # Construct the URL for the API request
    requests.get(url)  # Send the request to deactivate Pi-hole

def manage_led():
    """Manage the LED and update snooze status based on the snooze time."""
    snooze_time = int(get_snooze_time())  # Get the snooze time as an integer
    GPIO.output(LED_PIN, GPIO.HIGH)  # Turn on the LED
    #time.sleep(snooze_time + 2)  # Wait for the snooze duration plus a buffer
    #GPIO.output(LED_PIN, GPIO.LOW)  # Turn off the LED
    #update_snooze_status("inactive")  # Update the snooze status file

def update_snooze_status(status):
    """Update the snooze status file."""
    try:
        with open(STATUS_FILE, 'w') as file:
            file.write(status)
    except Exception as e:
        print(f"Error updating snooze status: {e}")

def display_snooze_time():
    """Display the snooze time on the LCD."""
    snooze_time = get_snooze_time()
    with display_lock:
        lcd.crlf()
        lcd.write_string(f"{snooze_time} seconds")

if __name__ == "__main__":
    # Run the rest of the script in separate threads to not block the display
    threading.Thread(target=display_snooze_time).start()
    threading.Thread(target=deactivate_pihole).start()
    threading.Thread(target=manage_led).start()
