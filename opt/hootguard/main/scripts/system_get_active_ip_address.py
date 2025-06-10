# Script Name: system_get_active_ip_address.py
# Version: 0.1
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script retrieves the active IP address of the system by using the system's hostname. It attempts to
# resolve the hostname to an IP address and returns the result. If an error occurs during the process, 
# it logs the error and returns `None`.

import socket
from .global_logger import logger

def get_pihole_ip():
    """Retrieve the active IP address of the system based on its hostname."""
    logger.debug("INFO - Retrieving the system's active IP address.")
    try:
        # Get the hostname of the system
        hostname = socket.gethostname()
        logger.debug(f"INFO - System hostname: {hostname}")
        
        # Get the IP address corresponding to the hostname
        ip_address = socket.gethostbyname(hostname)
        logger.debug(f"INFO - Active IP address: {ip_address}")

        return ip_address
    except Exception as e:
        logger.debug(f"ERROR - Failed to retrieve IP address: {e}")
        return None
