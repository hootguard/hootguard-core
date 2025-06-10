# Script Name: service_check_adblocker_status.py
# Version: 0.2
# Author: HootGuard
# Date: 23. February 2025

# Description:
# This script checks if the Pi-hole adblocker is actively blocking ads.
# It performs two checks:
# 1. Ensures the `pihole-FTL` service is running.
# 2. Uses `pihole status` to verify if ad blocking is enabled.
# If any of these checks fail, it reports the adblocker as inactive.

import subprocess
from .global_logger import logger

def check_adblocker_status():
    """Check if Pi-hole is actively blocking ads."""
    logger.debug("INFO - Checking Pi-hole adblocker status.")

    try:
        # Check if the Pi-hole FTL service is running
        ftl_status = subprocess.run(
            ['/usr/bin/sudo', 'systemctl', 'is-active', 'pihole-FTL'],
            stdout=subprocess.PIPE, text=True
        )
        if ftl_status.stdout.strip() != 'active':
            logger.debug("WARNING - Pi-hole-FTL service is NOT running.")
            return 'Inactive'

        # Check if Pi-hole ad blocking is enabled
        pihole_status = subprocess.run(
            ['/usr/bin/sudo', 'pihole', 'status'],
            stdout=subprocess.PIPE, text=True
        )

        # Look for "Pi-hole blocking is enabled" in the output
        if "Pi-hole blocking is enabled" in pihole_status.stdout:
            logger.debug("INFO - Pi-hole adblocker is active and blocking ads.")
            return 'Active'
        else:
            logger.debug("WARNING - Pi-hole is running but ad blocking is DISABLED.")
            return 'Inactive'

    except subprocess.CalledProcessError as e:
        logger.debug(f"ERROR - Failed to check Pi-hole status: {e}")
        return f'Failed to check Pi-hole service: {e}'
