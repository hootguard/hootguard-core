# Script Name: service_check_vpn_status.py
# Version: 0.2
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script checks the status of both WireGuard VPN services (`wg-quick@wg0` and `wg-quick@wg1`). It uses the `systemctl` 
# command to verify if the services are active, either running or exited. It returns:
# - "Active (wg0)" if only wg0 is active
# - "Active (wg1)" if only wg1 is active
# - "Active" if both services are active
# - "Inactive" if neither service is active
# If an error occurs while checking the status, it returns an error message.

import subprocess
from .global_logger import logger

def check_vpn_status():
    """Check the status of both WireGuard VPN services (wg-quick@wg0 and wg-quick@wg1)."""
    logger.debug("INFO - Checking VPN status for wg-quick@wg0 and wg-quick@wg1.")
    
    try:
        # Check the status of wg-quick@wg0
        wg0_result = subprocess.run(['/usr/bin/sudo', '/usr/bin/systemctl', 'status', 'wg-quick@wg0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        wg0_active = "Active: active (running)" in wg0_result.stdout or "Active: active (exited)" in wg0_result.stdout
        print(wg0_active)
        
        # Check the status of wg-quick@wg1
        wg1_result = subprocess.run(['/usr/bin/sudo', '/usr/bin/systemctl', 'status', 'wg-quick@wg1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        wg1_active = "Active: active (running)" in wg1_result.stdout or "Active: active (exited)" in wg1_result.stdout
        print(wg1_active)

        # Determine the combined status of wg0 and wg1
        if wg0_active and wg1_active:
            logger.info("INFO - Both wg-quick@wg0 and wg-quick@wg1 are active.")
            return "Active"
        elif wg0_active:
            logger.info("INFO - VPN service wg-quick@wg0 is active, wg-quick@wg1 is inactive.")
            return "Active (wg0)"
        elif wg1_active:
            logger.info("INFO - VPN service wg-quick@wg1 is active, wg-quick@wg0 is inactive.")
            return "Active (wg1)"
        else:
            logger.info("INFO - Both wg-quick@wg0 and wg-quick@wg1 are inactive.")
            return "Inactive"
    except Exception as e:
        logger.error(f"ERROR - Failed to check VPN status: {e}")
        return f"Failed to check VPN status: {e}"
