# Script Name: system_reboot.py
# Version: 0.1
# Author: HootGuard
# Date: 17. December 2024

# Description:
# This script triggers a system reboot by calling the `systemctl reboot` command using 
# elevated privileges (sudo). It logs a message to the console indicating the reboot process 
# has started. If the reboot command fails, it catches the error and prints an error message 
# with the reason for the failure.

import subprocess
from .global_logger import logger

def reboot():
    """Trigger a system reboot."""
    logger.info("Rebooting the system...")
    try:
        subprocess.run(["sudo", "/usr/bin/systemctl", "reboot"], check=True)
    except subprocess.CalledProcessError as e:
        logger.info(f"Failed to reboot: {e}")
