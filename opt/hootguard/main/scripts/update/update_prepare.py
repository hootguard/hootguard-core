# Script Name: update_prepare.py
# Version: 0.1
# Author: HootGuard
# Date: 17. December 2024

# Description:
# This script prepares the system for an update by setting an "update pending" flag file.
# The flag file indicates that an update should be executed after a system reboot. The file's 
# location and name are loaded from the global configuration file. If the operation is 
# successful, the script logs the status and returns `True`. If an error occurs, it logs the 
# error message and returns `False`

import os
import subprocess
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
UPDATE_PENDING_FLAG_FILE = config['update']['update_pending_flag']

#UPDATE_PENDING_FLAG_FILE = "/var/run/hootguard_update.flag"

def set_update_pending_flag():
    """Set the update flag."""
    logger.info("Setting update flag...")
    try:
        with open(UPDATE_PENDING_FLAG_FILE, "w") as flag:
            flag.write("update_pending")
        logger.info("Update flag set.")
        return True
    except Exception as e:
        logg.info(f"Failed to set update flag: {e}")
        return False
