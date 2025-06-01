# Script Name: service_check_ddns_status.py
# Version: 0.2
# Author: HootGuard
# Date: 24. February 2024

# Description:
# This script checks the DDNS service status by reading the content of the `ddns-status.txt` file.
# It determines whether the DDNS service is active or inactive based on the file's contents. If the 
# file is missing or contains invalid data, the script returns an error or an inactive status.


#from .global_config import DDNS_STATUS_FILE_PATH
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
DDNS_STATUS_FILE_PATH = config['ddns']['status_file']

def check_ddns_status():
    """
    Checks the DDNS service status based on the content of the ddns-status.txt file.

    Returns:
    - str: "Active" if the DDNS service is configured, "Inactive" otherwise, or an error message if the file is missing.
    """
    logger.debug(f"INFO - Checking DDNS status from {DDNS_STATUS_FILE_PATH}")
    try:
        with open(DDNS_STATUS_FILE_PATH, 'r') as file:
            status = file.read().strip()
            # Check if the status indicates an active DDNS service
            if status in ['UserHootDNS-ipv4', 'UserHootDNS-ipv6', 'UserDynu-ipv4', 'UserDynu-ipv6']:
                logger.debug(f"INFO - DDNS service is active with status: {status}")
                return "Active"
            elif status == 'NoConfiguration':
                logger.debug("INFO - DDNS service is inactive.")
                return "Inactive"
    except FileNotFoundError:
        # Handle the case where the ddns-status.txt file does not exist
        logger.debug("ERROR - ddns-status.txt file not found.")
        return "Error: ddns-status.txt file not found."

    # Return "Inactive" for any other content not explicitly checked for
    logger.debug("INFO - DDNS service is inactive with unknown status.")
    return "Inactive"
