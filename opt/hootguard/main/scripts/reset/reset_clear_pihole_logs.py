# Script Name: clear_pihole_logs.py
# Version: 0.2
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script clears all Pi-hole logs and resets the Pi-hole FTL database in the HootGuard system.
# - Truncates the DNS query log (`/var/log/pihole.log`) and FTL log (`/var/log/pihole-FTL.log`).
# - Stops the Pi-hole FTL service, removes the FTL database, and restarts the service to regenerate a fresh database.
# Logs the success or failure of each step, ensuring proper cleanup and regeneration of Pi-hole logs and database.
# Returns `True` on success, `False` otherwise.

import subprocess
import os
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Paths from the config
SECURE_RUN_FILE = config['misc']['secure_run_file']

# Load other variables
PIHOLE_LOG_PATH = "/var/log/pihole.log"
FTL_LOG_PATH = "/var/log/pihole-FTL.log"
FTL_DB_PATH = "/etc/pihole/pihole-FTL.db"

def clear_pihole_logs():
    try:
	# Flush pihole log and database
        subprocess.run(['pihole', '-f'], check=True)
        logger.info("Pi-hole log and databased flushed successfully.")

        # Clear DNS query log
        if os.path.exists(PIHOLE_LOG_PATH):
            subprocess.run(['/usr/bin/sudo', SECURE_RUN_FILE, 'clear-log', PIHOLE_LOG_PATH], check=True)
            logger.info(f"DNS query log {PIHOLE_LOG_PATH} cleared successfully.")
        else:
            logger.warning(f"DNS query log {PIHOLE_LOG_PATH} does not exist, skipping.")

        # Clear FTL log
        if os.path.exists(FTL_LOG_PATH):
            subprocess.run(['/usr/bin/sudo', SECURE_RUN_FILE, 'clear-log', FTL_LOG_PATH], check=True)
            logger.info(f"FTL log {FTL_LOG_PATH} cleared successfully.")
        else:
            logger.warning(f"FTL log {FTL_LOG_PATH} does not exist, skipping.")

        # Stop the FTL service
        subprocess.run(['/usr/bin/sudo', SECURE_RUN_FILE, 'stop-service', 'pihole-FTL'], check=True)
        logger.info("Pi-hole FTL service stopped successfully.")

        # Remove the Pi-hole FTL database
        if os.path.exists(FTL_DB_PATH):
            subprocess.run(['/usr/bin/sudo', SECURE_RUN_FILE, 'remove-file', FTL_DB_PATH], check=True)
            logger.info(f"FTL database {FTL_DB_PATH} removed successfully.")
        else:
            logger.warning(f"FTL database {FTL_DB_PATH} does not exist, skipping.")

        # Restart the FTL service, which will regenerate the database
        subprocess.run(['/usr/bin/sudo', SECURE_RUN_FILE, 'start-service', 'pihole-FTL'], check=True)
        logger.info("Pi-hole FTL service restarted successfully.")

        # If everything runs fine, return True
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        return False

    except Exception as e:
        logger.error(f"Error occurred while clearing Pi-hole logs: {e}")
        return False
