# Script Name: adblock_update_gravity_db.py
# Version: 0.1
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script updates Pi-hole's gravity database in the HootGuard system by running the Pi-hole command (`pihole -g`).
# The gravity database is used to block domains based on blocklists. The script logs success or failure messages
# based on the outcome of the update.

import subprocess
import logging
#from .global_logger import logger

# Configure logging
logging.basicConfig(filename='/var/log/hootguard_system.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

def update_gravity_db():
    """Update Pi-hole gravity."""
    success = True
    
    try:
        subprocess.run(['/usr/local/bin/pihole', '-g'], check=True)
        logging.info("INFO - Pi-hole gravity updated successfully.")
        subprocess.run(['/usr/local/bin/pihole', 'enable'], check=True)
        logging.info("INFO - Pi-hole successfully enabled.")
        return True
    except subprocess.SubprocessError as e:
        logging.info(f"ERROR - Error updating Pi-hole gravity: {str(e)}")
        return False

# Run the update function
update_gravity_db()
