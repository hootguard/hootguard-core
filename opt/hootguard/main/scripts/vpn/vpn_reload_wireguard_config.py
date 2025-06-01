# Script Name: vpn_reload_wireguard_config.py
# Version: 0.2
# Author: HootGuard
# Date: 3. October 2024

# Description:
# This script reloads the WireGuard configuration for a specified interface (e.g., wg0 or wg1). It first uses the 
# 'wg-quick strip' command to generate a stripped version of the WireGuard configuration and then synchronizes the 
# interface configuration using 'wg syncconf'. This allows changes made to the configuration files to take effect 
# without restarting the WireGuard service.

import subprocess
from scripts.global_logger import logger

def vpn_reload_wg_interface(interface):
    """Reload WireGuard configuration for the specified interface."""
    logger.debug(f"Reloading WireGuard configuration for interface: {interface}")

    try:
        # Step 1: Run 'wg-quick strip' command to get the stripped config
        strip_output = subprocess.run(
            ["wg-quick", "strip", interface],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        # Step 2: Use the output from 'wg-quick strip' as input to 'wg syncconf'
        result = subprocess.run(
            ["sudo", "wg", "syncconf", interface, "/dev/stdin"],  # Use /dev/stdin for input
            input=strip_output.stdout, text=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        logger.debug(f"{interface} reloaded successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.debug(f"Failed to reload {interface}. Error: {e.stderr}")
        return False
