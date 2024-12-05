# Script Name: unbound_update_root_hints.py
# Version: 0.3
# Author: HootGuard
# Date: 02. December 2024

# Description:
# This script updates the `root.hints` file used by the Unbound DNS resolver. 
# It checks if today is the first day of the month and, if so, downloads the latest 
# `named.root` file from the Internet Assigned Numbers Authority (IANA) website. 
# The file is saved to the `/var/lib/unbound/root.hints` location.
# The script logs the success or failure of the update process and skips the update 
# on any other day.

import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(filename='/var/log/hootguard_system.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

def update_root_hints():
    # Check if today is the first day of the month
    if datetime.now().day == 1:
        try:
            # Delegate the update to /usr/local/bin/hootguard
            result = subprocess.run(
                ['/usr/bin/sudo', '/usr/local/bin/hootguard', 'update-root-hints'],
                capture_output=True, text=True, check=True
            )
            logging.info(f"root.hints updated successfully. Output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logging.error(f"An error occurred while updating root.hints: {e.stderr}")
    else:
        logging.info("No root.hints update required today.")

# Run the update function
update_root_hints()
