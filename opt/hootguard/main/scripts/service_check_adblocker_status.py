# Script Name: check_adblocker_status.py
# Version: 0.1
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script checks the status of the Pi-hole `pihole-FTL` service to determine if the adblocker is active.
# It runs a system command using `systemctl is-active` and returns whether the Pi-hole adblocker is active or inactive.
# If an error occurs while checking the service status, the script returns an error message.

import subprocess
from .global_logger import logger

def check_adblocker_status():
    """Check the status of the Pi-hole adblocker service (pihole-FTL)."""
    logger.debug("INFO - Checking Pi-hole adblocker status.")

    try:
        result = subprocess.run(['/usr/bin/sudo', 'systemctl', 'is-active', 'pihole-FTL'], stdout=subprocess.PIPE, text=True)
        if result.stdout.strip() == 'active':
            logger.debug("INFO - Pi-hole adblocker is active.")
            return 'Active'
        else:
            logger.debug("INFO - Pi-hole adblocker is inactive.")
            return 'Inactive'
    except subprocess.CalledProcessError as e:
        logger.debug(f"ERROR - Failed to check Pi-hole service: {e}")
        return 'Failed to check Pi-hole service: {}'.format(e)
