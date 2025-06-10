# Script Name: reset_gpio_button.py
# Version: 0.7
# Author: HootGuard
# Date: 12. November 2024

# Description:
# This script is triggered when the reset button connected to GPIO 5 is pressed. It resets the static IP address
# back to DHCP, replaces the current web and Pi-hole passwords with the default passwords, and reboots the system.
# The script uses GPIO event detection to monitor the button press and execute the reset actions.

import RPi.GPIO as GPIO
import time
import logging
from scripts.global_config_loader import load_config
from scripts.reset_main import perform_reset

# Configure logging
logging.basicConfig(filename='/var/log/hootguard_system.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

# Load the global config
config = load_config()

# Pin Setup
RESET_BUTTON_PIN = 5 # GPIO 5
GPIO.setmode(GPIO.BCM) # BCM = GPIO numbering (BOARD = pin numbering)
GPIO.setup(RESET_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def on_reset_button_pressed(channel):
    """Handle reset button press event to reset IP and passwords, then reboot the system."""
    logging.info("INFO - Reset button pressed, initiating reset...")
    perform_reset("reset_button")  # Calls the reset function with "reset_button" option

# Add event detection
GPIO.add_event_detect(RESET_BUTTON_PIN, GPIO.FALLING, callback=on_reset_button_pressed, bouncetime=2000)

try:
    while True:
        time.sleep(10)  # Sleep for 10 seconds
finally:
    GPIO.cleanup()
    logging.info("INFO - GPIO cleanup completed.")
