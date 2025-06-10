# Script Name: ddns_update_hootdns_global_config.py
# Version: 0.1
# Author: HootGuard
# Date: 7. June 2025

# Description:
# This script updates the global_config.yaml file with the HootDNS subdomain and API key
# entered during the setup process. It ensures both values are written under the 'ddns'
# section of the configuration. The script handles missing keys gracefully and logs all actions.

import yaml
import os
from .global_logger import logger
from .global_config_loader import load_config

# Load global config
config = load_config()
GLOBAL_CONFIG_PATH = config['misc']['global_config_file']

def ddns_update_hootdns_credentials(subdomain: str, api_key: str) -> bool:
    """
    Update the HootDNS subdomain and API key in global_config.yaml.
    Returns True if successful, False otherwise.
    """
    logger.debug(f"INFO - Starting update of HootDNS credentials in {GLOBAL_CONFIG_PATH}")

    try:
        # Load existing config
        if not os.path.exists(GLOBAL_CONFIG_PATH):
            logger.error(f"ERROR - Global config file does not exist: {GLOBAL_CONFIG_PATH}")
            return False

        with open(GLOBAL_CONFIG_PATH, 'r') as f:
            config_data = yaml.safe_load(f)

        # Make sure ddns section exists
        if 'ddns' not in config_data:
            config_data['ddns'] = {}

        config_data['ddns']['user_hootdns_subdomain'] = subdomain
        config_data['ddns']['user_hootdns_api_key'] = api_key

        # Write back to file
        with open(GLOBAL_CONFIG_PATH, 'w') as f:
            yaml.safe_dump(config_data, f, default_flow_style=False)

        logger.info("HootDNS credentials successfully written to global_config.yaml")
        return True

    except Exception as e:
        logger.error(f"ERROR - Failed to update HootDNS credentials: {e}")
        return False
