# Script Name: ddns_update_status_file.py
# Version: 0.2
# Author: HootGuard
# Date: 23. August 2024

# Description:
# This script updates the DDNS status file in the HootGuard system. It sets the appropriate status based on 
# the selected DDNS option (e.g., HootGuard Cloudflare, User Cloudflare, or DuckDNS). The updated status 
# is written to the DDNS status file, and the script includes error handling for logging any issues.

#from .global_config import DDNS_STATUS_FILE_PATH
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
DDNS_STATUS_FILE_PATH = config['ddns']['status_file']

def ddns_update_status(option):
    """
    Updates the ddns_status.txt file based on the specified option.
    
    Parameters:
    - option (str): The DDNS option to set the status for.
    
    Returns:
    - bool: True if the status is updated successfully, False if an exception occurs.
    """
    try:
        status = ''
        
        if option == 'hootguard-cloudflare':
            status = 'HootGuardCloudflare'
        elif option == 'user-cloudflare-ipv4':
            status = 'UserCloudflare-ipv4'
        elif option == 'user-cloudflare-ipv6':
            status = 'UserCloudflare-ipv6'
        elif option == 'user-duckdns-ipv4':
            status = 'UserDuckDNS-ipv4'
        elif option == 'user-duckdns-ipv6':
            status = 'UserDuckDNS-ipv6'
        elif option == 'no-config':
            status = 'NoConfiguration'
        else:
            raise ValueError(f"Invalid option: {option}")

        with open(DDNS_STATUS_FILE_PATH, "w") as file:
            file.write(status)

        logger.debug(f"INFO - Successfully updated DDNS status to: {status}")
        return True

    except Exception as e:
        logger.error(f"ERROR - An error occurred while updating DDNS status: {str(e)}")
        return False
