# Script Name: ssh_control_service.py
# Version: 0.1
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script provides functions to control the SSH service on the system. It includes functionality to:
# - Check if the SSH service is active.
# - Enable the SSH service.
# - Disable the SSH service.
# If an error occurs during any of these operations, the script logs the error.

import subprocess
from .global_logger import logger

# Function to check if SSH is active
def check_ssh_status():
    """Check the status of the SSH service."""
    logger.debug("INFO - Checking SSH service status.")
    try:
        # Execute the systemctl command to check the status of the ssh service
        result = subprocess.run(['sudo', 'systemctl', 'status', 'ssh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check if the service is active (including the "active (exited)" state)
        if "Active: active (running)" in result.stdout or "Active: active (exited)" in result.stdout:
            logger.debug("INFO - SSH service is active.")
            return "Active"
        else:
            logger.debug("INFO - SSH service is inactive.")
            return "Inactive"
    except Exception as e:
        logger.error(f"ERROR - Failed to check SSH status: {e}")
        return False

# Function to enable SSH
def enable_ssh():
    """Enable the SSH service."""
    logger.debug("INFO - Enabling SSH service.")
    try:
        # Run systemctl to start the SSH service
        subprocess.run(['sudo', 'systemctl', 'start', 'ssh'], check=True)
        logger.info("INFO - SSH service enabled successfully.")
        return True
    except Exception as e:
        logger.error(f"ERROR - Error enabling SSH: {e}")
        return False

# Function to disable SSH
def disable_ssh():
    """Disable the SSH service."""
    logger.debug("INFO - Disabling SSH service.")
    try:
        # Run systemctl to stop the SSH service
        subprocess.run(['sudo', 'systemctl', 'stop', 'ssh'], check=True)
        logger.info("INFO - SSH service disabled successfully.")
        return True
    except Exception as e:
        logger.error(f"ERROR - Error disabling SSH: {e}")
        return False
