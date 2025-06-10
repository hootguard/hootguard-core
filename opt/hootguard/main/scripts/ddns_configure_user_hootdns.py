# Script Name: ddns_configure_user_hootdns.py
# Version: 0.1
# Author: HootGuard
# Date: 07. May 2025

# Description:
# This script updates the HOOTDNS Bash script file (either 'user-hootdns.sh' for IPv4 or the IPv6 equivalent) 
# with new key information. It facilitates dynamic modification of the key
# used for HootDNS updates, based on the IP version provided (IPv4 or IPv6).

import re
import subprocess
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
DDNS_USER_HOOTDNS_SCRIPT_PATH = config['ddns']['user_hootdns_script']
DDNS_USER_HOOTDNS_V6_SCRIPT_PATH = config['ddns']['user_hootdns_v6_script']

def ddns_activate_hootdns(ip_version, initial_setup=None):
    
    # Determine the file path based on the IP version
    if ip_version == "ipv4":
        script_path = DDNS_USER_HOOTDNS_SCRIPT_PATH
    elif ip_version == "ipv6":
        script_path = DDNS_USER_HOOTDNS_V6_SCRIPT_PATH
    else:
        logger.info("ERROR - Invalid IP version. Please specify 'ipv4' or 'ipv6'.")
        return False
    
    try:
        # Execute the HootDNS script
        subprocess.run(['/bin/bash', script_path], check=True)
        logger.info(f"SUCCESS - HootDNS {ip_version} script executed successfully.")
        return True
    except Exception as e:
        logger.info(f"ERROR - An error occurred while updating the HootDNS {ip_version} script: {e}")
        return False

# Run from command line
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./ddns_configure_user_hootdns.py [ipv4|ipv6]")
        sys.exit(1)
    ip_version = sys.argv[1]
    ddns_activate_hootdns(ip_version)
