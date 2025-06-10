# Script Name: vpn_get_primary_dns.py
# Version: 0.2
# Author: HootGuard
# Date: 3. October 2024

# Description:
# This script retrieves the primary IPv4 address assigned to the specified network interface (e.g., eth0). 
# It uses the 'ip addr show' command to get the IP address of the network interface defined by 'NETWORK_INTERFACE_1' 
# from 'scripts.global_config'. The IP address returned can be used as the primary DNS address in other configurations.

import subprocess
#from scripts.global_config import NETWORK_INTERFACE_1
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
NETWORK_INTERFACE_1 = config['network']['interface_1']

def get_primary_dns():
    """Get the IP address of the primary network interface."""
    try:
        result = subprocess.check_output(['ip', 'addr', 'show', NETWORK_INTERFACE_1]).decode('utf-8')
        for line in result.splitlines():
            if "inet " in line:
                logger.debug(f"Successfully extracted primary DNS from {NETWORK_INTERFACE_1}")
                return line.split()[1].split('/')[0]
    except subprocess.CalledProcessError as e:
        logger.debug(f"Failed to get primary DNS from {NETWORK_INTERFACE_1}: {str(e)}")
    return None
