# Script Name: vpn_remove_client_config.py
# Version: 0.1
# Author: HootGuard
# Date: 4. October 2024

# Description:
# This script removes the WireGuard client configuration file based on the client name.
# It ensures that the file is deleted from the directory specified by 'VPN_CONFIGS_PATH'.

import os
#from scripts.global_config import VPN_CONFIGS_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CONFIGS_PATH = config['vpn']['client_configs_path']

def remove_client_config(client_name):
    """Remove the client configuration file."""
    config_file = os.path.join(VPN_CONFIGS_PATH, f"{client_name}.conf")

    # Check if the config file exists and remove it
    if os.path.exists(config_file):
        try:
            os.remove(config_file)
            logger.debug(f"SUCCESS - Client configuration file for {client_name} removed.")
            return True
        except OSError as e:
            logger.debug(f"ERROR - Failed to remove client configuration file for {client_name}: {str(e)}")
            return False
    else:
        logger.debug(f"ERROR - Client configuration file for {client_name} does not exist.")
        return False
