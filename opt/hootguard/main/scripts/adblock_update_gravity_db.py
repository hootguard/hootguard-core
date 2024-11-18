# Script Name: adblock_update_gravity_db.py
# Version: 0.1
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script updates Pi-hole's gravity database in the HootGuard system by running the Pi-hole command (`pihole -g`).
# The gravity database is used to block domains based on blocklists. The script logs success or failure messages
# based on the outcome of the update.

import subprocess
from .global_logger import logger

def update_gravity_db():
    """Update Pi-hole gravity."""
    success = True
    
    try:
        subprocess.run(['pihole', '-g'], check=True)
        logger.debug("INFO - Pi-hole gravity updated successfully.")
        return True
    except subprocess.SubprocessError as e:
        logger.debug(f"ERROR - Error updating Pi-hole gravity: {str(e)}")
        return False
