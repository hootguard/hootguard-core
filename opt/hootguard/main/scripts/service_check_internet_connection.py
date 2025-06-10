# Script Name: check_internet_connection.py
# Version: 0.1
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script checks for an active internet connection by pinging two well-known DNS servers (1.1.1.1 and 8.8.8.8).
# It returns 'OK' if either ping succeeds, indicating that an internet connection is available. If both pings fail,
# it returns 'No internet connection'

import subprocess
from .global_logger import logger

def ping(host):
    """
    Returns True if host responds to a ping request
    """
    logger.debug(f"INFO - Pinging {host}")
    command = ['ping', '-c', '1', host]
    return subprocess.call(command) == 0

def check_internet_connection():
    """
    Attempts to ping 1.1.1.1, and if it fails, tries 8.8.8.8.
    Returns 'OK' if any ping succeeds, otherwise 'No internet connection'.
    """
    logger.debug("INFO - Checking internet connection.")
    if ping('1.1.1.1'):
        logger.debug("INFO - Internet connection OK (ping to 1.1.1.1 succeeded).")
        return 'OK'
    elif ping('8.8.8.8'):
        logger.debug("INFO - Internet connection OK (ping to 8.8.8.8 succeeded).")
        return 'OK'
    else:
        logger.debug("WARNING - No internet connection (pings to both 1.1.1.1 and 8.8.8.8 failed).")
        return 'No internet connection'
