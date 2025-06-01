# Script Name: ddns_configure_user_hootdns.py
# Version: 0.1
# Author: HootGuard
# Date: 07. May 2025

# Description:
# This script updates the DYNU Bash script file (either 'user-dynu.sh' for IPv4 or the IPv6 equivalent) 
# with new key information. It facilitates dynamic modification of the key
# used for DYNU updates, based on the IP version provided (IPv4 or IPv6).

import re
import subprocess
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
DDNS_USER_DYNU_SCRIPT_PATH = config['ddns']['user_hootdns_script']
DDNS_USER_DYNU_V6_SCRIPT_PATH = config['ddns']['user_hootdns_v6_script']

def ddns_activate_hootdns(ip_version, initial_setup=None):
    
    # Determine the file path based on the IP version
    if ip_version == "ipv4":
        script_path = DDNS_USER_DYNU_SCRIPT_PATH
    elif ip_version == "ipv6":
        script_path = DDNS_USER_DYNU_V6_SCRIPT_PATH
    else:
        logger.debug("ERROR - Invalid IP version. Please specify 'ipv4' or 'ipv6'.")
        return False
    
    try:
        # Execute the HootDNS script
        subprocess.run(['/bin/bash', script_path], check=True)
        logger.debug(f"SUCCESS - HootDNS {ip_version} script executed successfully.")
        return True
    except Exception as e:
        logger.debug(f"ERROR - An error occurred while updating the HootDNS {ip_version} script: {e}")
        return False
