# Script Name: ddns_read_status.py
# Version: 0.2
# Author: HootGuard
# Date: 14. August 2024

# Description:
# This script reads the current DDNS status from the specified status file in the HootGuard system. 
# It checks for the existence of the status file and maps the status code found in the file to a 
# corresponding status message. If the file is not found, the script defaults to indicating that no 
# configuration exists, and DDNS is inactive.

#from .global_config import DDNS_STATUS_FILE_PATH
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
DDNS_STATUS_FILE_PATH = config['ddns']['status_file']

def ddns_read_status_and_return_status():
    """Read the DDNS status from the status file and return the corresponding status message."""
    logger.debug(f"INFO - Reading DDNS status from {DDNS_STATUS_FILE_PATH}")
    try:
        with open(DDNS_STATUS_FILE_PATH, 'r') as file:
            status = file.read().strip()
            logger.debug(f"INFO - Read status: {status}")
    except FileNotFoundError:
        status = 'NoConfiguration'  # Assume no configuration if the file doesn't exist
        logger.debug("ERROR - DDNS status file not found. Defaulting to 'NoConfiguration'")

    # Map the status to the corresponding message
    status_message_map = {
        'UserHootDNS-ipv4': 'HootDNS (IPv4)',
        'UserHootDNS-ipv6': 'HootDNS (IPv6)',
        'UserDynu-ipv4': 'Personal Dynu DDNS (IPv4)',
        'UserDynu-ipv6': 'Personal Dynu DDNS (IPv6)',
        'NoConfiguration': 'DDNS inactive'
    }

    return status_message_map.get(status, 'DDNS inactive')  # Default to 'DDNS deactive' if status is unknown
