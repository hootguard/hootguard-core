# Script Name: pihole_get_api_key.py
# Version: 0.1
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script retrieves the API key from the Pi-hole configuration file (`/etc/pihole/setupVars.conf`).
# It searches for the 'WEBPASSWORD' parameter, which stores the API key, and returns it. The 
# `get_pihole_api_key()` function can be imported into other scripts to easily access the Pi-hole API key.

#from .global_config import PIHOLE_SETUP_VARS_PATH
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
PIHOLE_SETUP_VARS_PATH = config['pihole']['setup_vars_path']

def get_pihole_api_key():
    """Retrieve the Pi-hole API key from the setupVars.conf file."""
    logger.debug(f"INFO - Retrieving Pi-hole API key from {PIHOLE_SETUP_VARS_PATH}")

    api_key = None
    try:
        with open(PIHOLE_SETUP_VARS_PATH, "r") as f:
            for line in f:
                if line.startswith("WEBPASSWORD="):
                    api_key = line.split("=")[1].strip()
                    logger.debug("INFO - Pi-hole API key successfully retrieved.")
                    break
    except FileNotFoundError as e:
        logger.debug(f"ERROR - Pi-hole configuration file not found: {e}")
    except Exception as e:
        logger.debug(f"ERROR - Unexpected error while retrieving API key: {e}")
    return api_key
