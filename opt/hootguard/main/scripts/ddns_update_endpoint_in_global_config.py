# Script Name: ddns_update_endpoint_in_yaml.py
# Version: 0.2
# Author: HootGuard
# Date: 8. October 2024

# Description:
# This script updates the VPN endpoint in the global YAML configuration file used by the HootGuard system.
# It reads the YAML file, updates the "vpn.endpoint" entry with a new endpoint, and writes the changes back to the file.
# The script includes error handling to manage any issues during the file reading and writing process.

import yaml
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
GLOBAL_CONFIG_FILE_PATH = config['misc']['global_config_file']

# Function to replace the VPN endpoint in the YAML config file
def replace_vpn_endpoint(new_endpoint):
    """Replace the VPN endpoint in the YAML configuration file."""
    try:
        logger.debug(f"INFO - Replacing VPN endpoint in {GLOBAL_CONFIG_FILE_PATH} with new endpoint: {new_endpoint}")

        # Read the YAML configuration file
        with open(GLOBAL_CONFIG_FILE_PATH, 'r') as file:
            config = yaml.safe_load(file)

        # Update the VPN endpoint
        config['vpn']['endpoint'] = new_endpoint
        logger.debug(f"INFO - Updated VPN endpoint to: {new_endpoint}")

        # Write the updated config back to the YAML file
        with open(GLOBAL_CONFIG_FILE_PATH, 'w') as file:
            yaml.safe_dump(config, file, default_flow_style=False)
        
        logger.debug("INFO - VPN endpoint replacement successful.")
        return True

    except Exception as e:
        logger.error(f"ERROR - Error occurred while replacing VPN endpoint: {str(e)}")
        return False
