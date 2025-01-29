# Script Name: ddns_configure_user_ipv64.py
# Version: 0.2
# Author: HootGuard
# Date: 24. January 2025

# Description:
# This script updates the IPV64 Bash script file (either 'user-ipv64.sh' for IPv4 or the IPv6 equivalent) 
# with new key information. It facilitates dynamic modification of the key
# used for IPv64 updates, based on the IP version provided (IPv4 or IPv6).

import re
import subprocess
from .ddns_update_endpoint_in_global_config import replace_vpn_endpoint
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
DDNS_USER_IPV64_SCRIPT_PATH = config['ddns']['user_ipv64_script']
DDNS_USER_IPV64_V6_SCRIPT_PATH = config['ddns']['user_ipv64_v6_script']

def ddns_write_and_activate_ipv64(domain, key, ip_version, initial_setup=None):
    # Update the respective IPv64 script file (IPv4 or IPv6) with the new key.
    
    # Determine the file path based on the IP version
    if ip_version == "ipv4":
        script_path = DDNS_USER_IPV64_SCRIPT_PATH
    elif ip_version == "ipv6":
        script_path = DDNS_USER_IPV64_V6_SCRIPT_PATH
    else:
        logger.debug("ERROR - Invalid IP version. Please specify 'ipv4' or 'ipv6'.")
        return False
    
    try:
        # Open the existing IPV64 script
        with open(script_path, 'r') as file:
            content = file.read()

        # Replace the KEY= line with the new key using regex
        updated_content = re.sub(r'^KEY=.*$', f'KEY="{key}"', content, flags=re.MULTILINE)
        updated_content = re.sub(r'^DOMAIN=.*$', f'DOMAIN="{domain}"', updated_content, flags=re.MULTILINE)

        # Write the updated content back to the file
        with open(script_path, 'w') as file:
            file.write(updated_content)
        logger.debug(f"SUCCESS - IPv64 {ip_version} script updated successfully.")

        # Only run the following lines if this is not part of the initial_setup procedure
        if not initial_setup:
            # Update the endpoint in the global_config.yaml file to the new record_name
            if replace_vpn_endpoint(domain):
                logger.debug("SUCCESS - VPN endpoint updated successfully in global_config.yaml.")
            else:
                logger.debug("ERROR - Failed to update endpoint in global_config.yaml.")

            # Execute the updated IPv64 script
            subprocess.run(['/bin/bash', script_path], check=True)
            logger.debug(f"SUCCESS - IPv64 {ip_version} script executed successfully.")

        return True
    except Exception as e:
        logger.debug(f"ERROR - An error occurred while updating the IPV64 {ip_version} script: {e}")
        return False
